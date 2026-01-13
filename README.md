# 🐳 Docker Run 到 Docker Compose 转换器

**一行命令，自动生成 docker-compose.yml！**

## 🚀 快速开始

### 1️⃣ 创建文件
创建 `docker run.txt` 文件，写入你的 docker run 命令：

```txt
docker run --name redis -p 6379:6379 -d redis
docker run --name web -p 80:80 --link redis:db -d nginx
```

### 2️⃣ 运行转换
```bash
python run_to_compose.py
```

### 3️⃣ 获取结果
自动生成 `docker-compose.yml` 文件！ ✨

## 💡 使用示例

**输入：**
```txt
docker run --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=secret -v mysql_data:/var/lib/mysql -d mysql:8
docker run --name app -p 3000:3000 --link mysql:db -v ./app:/app -e NODE_ENV=prod -d node:14
```

**输出：**
```yaml
# Docker Compose 配置文件
# 由 Docker Run 到 Docker Compose 转换器生成

version: '3.9'
services:
  mysql:
    image: mysql:8
    container_name: mysql
    ports:
    - 3306:3306
    environment:
      MYSQL_ROOT_PASSWORD: secret
    volumes:
    - mysql_data:/var/lib/mysql
  app:
    image: node:14
    container_name: app
    ports:
    - 3000:3000
    environment:
      NODE_ENV: prod
    volumes:
    - ./app:/app
    links:
    - mysql:db
networks:
  default:
    driver: bridge
```

## 🎯 支持的参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--name` | 容器名称 | `--name myapp` |
| `-p` | 端口映射 | `-p 8080:80` |
| `-v` | 卷挂载 | `-v ./data:/app/data` |
| `-e` | 环境变量 | `-e NODE_ENV=prod` |
| `--restart` | 重启策略 | `--restart unless-stopped` |
| `--memory` | 内存限制 | `--memory 512m` |
| `--cpus` | CPU限制 | `--cpus 1.0` |
| `--network` | 网络配置 | `--network mynet` |
| `--link` | 容器链接 | `--link db:database` |
| `--privileged` | 特权模式 | `--privileged` |
| `--log-driver` | 日志驱动 | `--log-driver json-file` |
| `--health-cmd` | 健康检查 | `--health-cmd 'curl -f http://localhost'` |

## 📦 安装

```bash
pip install -r requirements.txt
```

## 🔥 核心特性

- ✅ **智能识别**：自动识别多个 docker run 命令
- ✅ **参数完整**：支持几乎所有 docker run 参数
- ✅ **服务命名**：智能从镜像名生成服务名
- ✅ **中文友好**：输出带中文注释的配置文件
- ✅ **一键转换**：3步完成转换

## 💡 提示

- 每个 docker run 命令可以写在单独的行
- 支持复杂的参数组合
- 自动处理命名卷和绑定卷
- 生成标准的 Docker Compose v3.9 格式

开始使用，让容器编排更简单！ 🚀