# What If · 看山平行宇宙

知乎黑客松 MVP 项目。通过知乎行为轨迹与本地 mock 数据，推演用户被内容长期影响后的认知星尘、主宇宙、平行宇宙与半山宇宙广场。

## 目录结构

```text
what-if-universe/
├── frontend/    # Vue3 + Vite 前端应用，部署到 Vercel
├── backend/     # FastAPI 后端服务，部署到 Render
├── mock-data/   # Markdown mock 数据
├── README.md
├── package.json # 根目录统一脚本，方便本地运行和 Vercel 构建
├── render.yaml  # Render Blueprint 配置
└── vercel.json  # Vercel 前端部署配置
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
ARK_API_KEY=你的字节Ark API Key
ZHIHU_ACCESS_SECRET=你的知乎开放平台 Access Secret
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

本地 `.env`：

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

## 部署方案

当前推荐：

- 前端：Vercel
- 后端：Render

### 1. 部署后端到 Render

1. 将代码 push 到 GitHub。
2. 打开 Render，选择 `New +` -> `Blueprint`。
3. 选择这个 GitHub 仓库。
4. Render 会读取根目录 `render.yaml`，创建 `kanshan-universe-backend`。
5. 在 Render 服务 Environment 中添加：

```env
LLM_PROVIDER=ark
ARK_API_KEY=你的字节Ark API Key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=doubao-seed-1-6-flash-250828
ARK_FALLBACK_MODELS=doubao-seed-1-6-flash-250828
ZHIHU_ACCESS_SECRET=你的知乎开放平台 Access Secret
ZHIHU_SEARCH_URL=https://developer.zhihu.com/api/v1/content/zhihu_search
CORS_ALLOW_ORIGINS=https://你的-vercel-域名.vercel.app
```

部署完成后测试：

```text
https://你的-render-service.onrender.com/health
```

### 2. 部署前端到 Vercel

1. 打开 Vercel，导入同一个 GitHub 仓库。
2. Framework Preset 选择 `Vite` 或保持自动识别。
3. Root Directory 保持仓库根目录。
4. Vercel 会使用根目录 `vercel.json`：

```json
{
  "installCommand": "npm install",
  "buildCommand": "npm run build",
  "outputDirectory": "dist"
}
```

5. 在 Vercel Environment Variables 添加：

```env
VITE_API_BASE_URL=https://你的-render-service.onrender.com
```

6. 部署完成后，把最终 Vercel 域名回填到 Render 的：

```env
CORS_ALLOW_ORIGINS=https://你的-vercel-域名.vercel.app
```

然后重新部署一次 Render 后端。

## 部署检查

后端健康检查：

```text
https://你的-render-service.onrender.com/health
```

前端需要确认：

- Landing Page 可以进入信件页
- 游客进入可以进入主宇宙
- 创建人生星尘可以调用后端
- What If 平行宇宙可以调用后端
- 知乎搜索链接能出现在节点旁
- 分享到宇宙广场只写入浏览器 localStorage

## 重要说明

- 不要提交 `backend/.env`。
- 前端新增星尘、平行宇宙星尘、分享到广场的数据，目前都只存在用户浏览器 localStorage。
- Render Free 服务冷启动会比较慢，首次系统推演可能需要等待几十秒。
