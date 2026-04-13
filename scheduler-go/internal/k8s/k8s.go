package k8s

import (
	"bytes"
	"context"
	"fmt"
	"log"
	"math/rand"
	"strings"
	"sync"

	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/kubernetes/scheme"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/tools/remotecommand"

	"openclaw-scheduler/internal/models"
)

var (
	clientset          *kubernetes.Clientset
	restConfig         *rest.Config
	poolStatus         = make(map[string]PoolStatus)
	agentSessions      = make(map[string]string)
	agentRegistrations = make(map[string]string)
	mu                 sync.RWMutex
	initialized        bool
	initMu             sync.RWMutex
)

type PoolStatus struct {
	Status    string `json:"status"` // idle, busy
	AgentID   string `json:"agent_id"`
	Allocated int64  `json:"allocated_at"`
}

// IsInitialized 检查 K8s 客户端是否已初始化
func IsInitialized() bool {
	initMu.RLock()
	defer initMu.RUnlock()
	return initialized
}

// InitK8s 初始化 K8s 客户端
func InitK8s() error {
	initMu.Lock()
	defer initMu.Unlock()

	var err error

	// 尝试集群内配置
	restConfig, err = rest.InClusterConfig()
	if err != nil {
		// 尝试本地配置
		kubeconfig := clientcmd.NewDefaultClientConfigLoadingRules().GetDefaultFilename()
		restConfig, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
		if err != nil {
			return fmt.Errorf("无法创建 K8s 配置: %v", err)
		}
	}

	clientset, err = kubernetes.NewForConfig(restConfig)
	if err != nil {
		return fmt.Errorf("无法创建 K8s 客户端: %v", err)
	}

	log.Println("✅ K8s 客户端初始化成功")
	initialized = true
	return nil
}

// ExecCommand 在 Pod 中执行命令
func ExecCommand(namespace, podName string, command []string) (string, string, error) {
	req := clientset.CoreV1().RESTClient().Post().
		Resource("pods").
		Name(podName).
		Namespace(namespace).
		SubResource("exec")

	option := &corev1.PodExecOptions{
		Command: command,
		Stdin:   false,
		Stdout:  true,
		Stderr:  true,
		TTY:     false,
	}

	req.VersionedParams(option, scheme.ParameterCodec)

	exec, err := remotecommand.NewSPDYExecutor(restConfig, "POST", req.URL())
	if err != nil {
		return "", "", fmt.Errorf("创建 executor 失败: %v", err)
	}

	var stdout, stderr bytes.Buffer
	err = exec.StreamWithContext(context.Background(), remotecommand.StreamOptions{
		Stdout: &stdout,
		Stderr: &stderr,
	})

	if err != nil {
		return stdout.String(), stderr.String(), fmt.Errorf("执行命令失败: %v", err)
	}

	return stdout.String(), stderr.String(), nil
}

// AllocateContainerByKernel 根据内核类型分配容器
func AllocateContainerByKernel(kernelType, agentID string) (*models.ContainerStatus, error) {
	// 检查 K8s 客户端是否已初始化
	if !IsInitialized() {
		return nil, fmt.Errorf("K8s 客户端尚未初始化，请稍后重试")
	}

	// 根据内核类型确定 label selector
	var labelSelector string
	switch kernelType {
	case "openclaw":
		labelSelector = "app=openclaw-pool"
	case "qwenpaw":
		labelSelector = "app=qwenpaw-pool"
	default:
		// 默认使用 openclaw
		labelSelector = "app=openclaw-pool"
		log.Printf("⚠️  [AllocateContainerByKernel] 未知内核类型 %s，使用 openclaw", kernelType)
	}

	log.Printf("🔧 [AllocateContainerByKernel] 内核类型: %s, LabelSelector: %s", kernelType, labelSelector)
	return allocateContainerWithSelector(agentID, labelSelector)
}

// AllocateContainer 分配容器（保留原接口，默认使用 OpenClaw）
func AllocateContainer(agentID string) (*models.ContainerStatus, error) {
	return AllocateContainerByKernel("openclaw", agentID)
}

// allocateContainerWithSelector 根据 label selector 分配容器
func allocateContainerWithSelector(agentID, labelSelector string) (*models.ContainerStatus, error) {
	mu.Lock()
	defer mu.Unlock()

	// 检查是否有现有会话
	if podName, exists := agentSessions[agentID]; exists {
		// 验证 Pod 是否还存在
		pod, err := clientset.CoreV1().Pods("openclaw").Get(context.TODO(), podName, metav1.GetOptions{})
		if err == nil && pod.Status.Phase == "Running" {
			return &models.ContainerStatus{
				PodName: podName,
				Status:  "reused",
				AgentID: agentID,
				Phase:   string(pod.Status.Phase),
				IP:      pod.Status.PodIP,
				Node:    pod.Spec.NodeName,
			}, nil
		}
		// Pod 不存在，清理
		delete(agentSessions, agentID)
		delete(poolStatus, podName)
	}

	// 获取指定 label 的 Pod
	pods, err := clientset.CoreV1().Pods("openclaw").List(context.TODO(), metav1.ListOptions{
		LabelSelector: labelSelector,
	})
	if err != nil {
		return nil, fmt.Errorf("获取 Pod 列表失败: %v", err)
	}

	// 找到空闲的 Pod
	var idlePods []string
	for _, pod := range pods.Items {
		if pod.Status.Phase == "Running" {
			podName := pod.Name
			status, exists := poolStatus[podName]
			if !exists || status.Status == "idle" {
				idlePods = append(idlePods, podName)
			}
		}
	}

	if len(idlePods) == 0 {
		return nil, fmt.Errorf("没有可用的容器")
	}

	// 随机选择一个
	selectedPod := idlePods[rand.Intn(len(idlePods))]

	// 更新状态
	poolStatus[selectedPod] = PoolStatus{
		Status:    "busy",
		AgentID:   agentID,
		Allocated: 0, // 时间戳
	}
	agentSessions[agentID] = selectedPod

	// 获取 Pod 详细信息
	pod, _ := clientset.CoreV1().Pods("openclaw").Get(context.TODO(), selectedPod, metav1.GetOptions{})

	return &models.ContainerStatus{
		PodName: selectedPod,
		Status:  "allocated",
		AgentID: agentID,
		Phase:   string(pod.Status.Phase),
		IP:      pod.Status.PodIP,
		Node:    pod.Spec.NodeName,
	}, nil
}

func EnsureAgentReady(agentID string, container *models.ContainerStatus) error {
	mu.RLock()
	registeredPod, exists := agentRegistrations[agentID]
	mu.RUnlock()

	if exists && registeredPod == container.PodName {
		return nil
	}

	agentDir := fmt.Sprintf("/data/agents/%s/agent", agentID)
	workspaceDir := fmt.Sprintf("/data/agents/%s", agentID)
	addCmd := []string{"node", "openclaw.mjs", "agents", "add", agentID, "--workspace", workspaceDir, "--agent-dir", agentDir, "--non-interactive"}

	stdout, stderr, err := ExecCommand("openclaw", container.PodName, addCmd)
	if err != nil {
		if strings.Contains(stderr, "already exists") {
			mu.Lock()
			agentRegistrations[agentID] = container.PodName
			mu.Unlock()
			return nil
		}
		return fmt.Errorf("准备智能体失败: %v, stdout: %s, stderr: %s", err, stdout, stderr)
	}

	mu.Lock()
	agentRegistrations[agentID] = container.PodName
	mu.Unlock()

	return nil
}

func WarmAgent(agentID string) (*models.ContainerStatus, error) {
	container, err := AllocateContainer(agentID)
	if err != nil {
		return nil, err
	}

	if err := EnsureAgentReady(agentID, container); err != nil {
		return nil, err
	}

	return container, nil
}

// ReleaseContainer 释放容器
func ReleaseContainer(podName, agentID string) {
	mu.Lock()
	defer mu.Unlock()

	if _, exists := poolStatus[podName]; exists {
		poolStatus[podName] = PoolStatus{
			Status:  "idle",
			AgentID: "",
		}
	}

	if agentID != "" {
		delete(agentSessions, agentID)
	}
}

// GetPoolStatus 获取容器池状态
func GetPoolStatus() (map[string]interface{}, error) {
	mu.RLock()
	defer mu.RUnlock()

	pods, err := clientset.CoreV1().Pods("openclaw").List(context.TODO(), metav1.ListOptions{
		LabelSelector: "app=openclaw-pool",
	})
	if err != nil {
		return nil, err
	}

	var podInfos []models.ContainerStatus
	for _, pod := range pods.Items {
		status, exists := poolStatus[pod.Name]
		if !exists {
			status = PoolStatus{Status: "idle", AgentID: ""}
		}

		podInfos = append(podInfos, models.ContainerStatus{
			PodName: pod.Name,
			Status:  status.Status,
			AgentID: status.AgentID,
			Phase:   string(pod.Status.Phase),
			IP:      pod.Status.PodIP,
			Node:    pod.Spec.NodeName,
		})
	}

	return map[string]interface{}{
		"pool_status":       poolStatus,
		"agent_sessions":    agentSessions,
		"registered_agents": agentRegistrations,
		"pods":              podInfos,
		"total_pods":        len(pods.Items),
	}, nil
}
