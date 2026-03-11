# Kubernetes 部署指南

## 部署架构

```
Kubernetes 集群
├── Namespace: openclaw
├── Deployment: openclaw-{instance}
├── Service: openclaw-{instance}-svc
└── ConfigMap: openclaw-{instance}-config
```

## 部署步骤

### 1. 创建命名空间

```bash
kubectl create namespace openclaw
```

### 2. 应用配置

```bash
kubectl apply -f templates/kubernetes/deployment.yaml
kubectl apply -f templates/kubernetes/service.yaml
kubectl apply -f templates/kubernetes/configmap.yaml
```

### 3. 查看状态

```bash
kubectl get pods -n openclaw
kubectl get svc -n openclaw
```

## 持久化存储

使用 PersistentVolumeClaim 存储工作空间：

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: openclaw-prod-01-workspace
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

## 扩缩容

```bash
kubectl scale deployment openclaw-prod-01 --replicas=3 -n openclaw
```

## 日志查看

```bash
kubectl logs -f deployment/openclaw-prod-01 -n openclaw
```
