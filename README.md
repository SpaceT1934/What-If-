# What If · 看山平行宇宙

知乎黑客松 MVP 项目。通过知乎行为轨迹与本地 mock 数据，推演用户被内容长期影响后的认知星尘、主宇宙、平行宇宙与半山宇宙广场。

## 目录结构

```text
what-if-universe/
├── frontend/     # Vue3 + Vite 前端
├── backend/      # FastAPI 后端
├── mock-data/    # Markdown mock 数据，后端会读取
├── Dockerfile    # 腾讯云 CloudBase 云托管后端容器
├── .dockerignore
├── package.json  # 根目录前端构建脚本
├── vercel.json   # 可选：Vercel 前端配置
├── render.yaml   # 可选：Render 后端配置
└── README.md
```

## 本地运行

### 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

在 `backend/.env` 填入：

```env
LLM_PROVIDER=ark
ARK_API_KEY=你的字节 Ark API Key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=doubao-seed-1-6-flash-250828
ARK_FALLBACK_MODELS=doubao-seed-1-6-flash-250828
ZHIHU_ACCESS_SECRET=你的知乎开放平台 Access Secret
ZHIHU_SEARCH_URL=https://developer.zhihu.com/api/v1/content/zhihu_search
ZHIHU_OAUTH_APP_ID=你的知乎 OAuth App ID
ZHIHU_OAUTH_APP_KEY=你的知乎 OAuth App Key
ZHIHU_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/api/auth/zhihu/callback
FRONTEND_BASE_URL=http://127.0.0.1:5173
CORS_ALLOW_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

启动：

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 前端

```bash
cd frontend
npm install
cp .env.example .env
```

本地 `frontend/.env`：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

启动：

```bash
npm run dev
```

访问：

```text
http://127.0.0.1:5173
```

## 腾讯云 CloudBase 部署

推荐现在使用：

- 前端：CloudBase 静态网站托管 / Web 应用托管
- 后端：CloudBase 云托管

### 1. 部署后端到 CloudBase 云托管

后端用根目录 `Dockerfile` 部署。注意不要选择 `backend/` 作为构建根目录，因为后端需要读取根目录的 `mock-data/`。

CloudBase 云托管配置建议：

```text
代码目录 / 构建目录：仓库根目录
构建方式：Dockerfile
Dockerfile 路径：Dockerfile
服务端口：3000
公网访问：开启
```

环境变量：

```env
LLM_PROVIDER=ark
ARK_API_KEY=你的字节 Ark API Key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=doubao-seed-1-6-flash-250828
ARK_FALLBACK_MODELS=doubao-seed-1-6-flash-250828
ZHIHU_ACCESS_SECRET=你的知乎开放平台 Access Secret
ZHIHU_SEARCH_URL=https://developer.zhihu.com/api/v1/content/zhihu_search
ZHIHU_OAUTH_APP_ID=你的知乎 OAuth App ID
ZHIHU_OAUTH_APP_KEY=你的知乎 OAuth App Key
ZHIHU_OAUTH_REDIRECT_URI=https://你的后端域名/api/auth/zhihu/callback
FRONTEND_BASE_URL=https://你的前端域名
CORS_ALLOW_ORIGINS=https://你的前端域名
```

后端部署成功后，访问：

```text
https://你的-cloudbase-后端域名/health
```

能看到健康检查返回，就说明后端可用。

### 2. 部署前端到 CloudBase

前端使用仓库根目录构建即可，根目录 `package.json` 会自动进入 `frontend/` 构建，并把产物同步到根目录 `dist/`。

CloudBase 前端构建配置：

```text
安装命令：npm install
构建命令：npm run build
发布目录：dist
```

前端环境变量：

```env
VITE_API_BASE_URL=https://你的-cloudbase-后端域名
```

如果 CloudBase 的前端环境变量没有在构建时生效，也可以在 `frontend/.env.production` 里写入同样内容后再部署，但不要把真实密钥放进前端。

### 3. 回填 CORS

前端部署完成后，拿到前端域名，例如：

```text
https://你的前端域名
```

回到 CloudBase 后端云托管，把环境变量改成：

```env
CORS_ALLOW_ORIGINS=https://你的前端域名,http://localhost:5173,http://127.0.0.1:5173
```

然后重新部署后端。

## 部署检查

1. 打开后端健康检查：

```text
https://你的-cloudbase-后端域名/health
```

2. 打开前端页面：

```text
https://你的-cloudbase-前端域名
```

3. 测试以下功能：

- 游客进入主宇宙
- 创建人生星尘
- What If 平行宇宙推演
- 节点旁知乎搜索链接
- 分享星尘到宇宙广场

## 不要上传 / 不要打包

```text
backend/.env
backend/.env.save
backend/.venv/
backend/__pycache__/
frontend/node_modules/
frontend/dist/
dist/
frontend/public/model/kanshan.glb
```

`frontend/public/model/kanshan.glb` 当前约 70MB，GitHub 网页上传会失败。先不上传也可以，只会影响阶段看山 3D 模型展示，不影响核心功能。
