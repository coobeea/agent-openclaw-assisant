FROM golang:1.22-alpine AS builder

ENV GOPROXY=https://goproxy.cn,direct

WORKDIR /app

# 复制 go mod 文件
COPY go.mod go.sum* ./
RUN go mod download

# 复制源代码
COPY . .

# 构建
RUN CGO_ENABLED=0 GOOS=linux go build -o scheduler ./cmd/server

# 最终镜像
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

# 从构建器复制二进制文件
COPY --from=builder /app/scheduler .

# 创建智能体工作空间目录
RUN mkdir -p /data/agents

EXPOSE 8080

CMD ["./scheduler"]
