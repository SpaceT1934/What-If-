# Backend

FastAPI 后端服务，负责游客模式下的系统推演、人生星尘生成、What If 平行宇宙推演，以及知乎开放平台搜索结果接入。

## 接口

- `GET /health`
- `GET /api/debug/llm-auth`
- `POST /api/guest/analyze`
- `POST /api/guest/generate-stardust`
- `POST /api/guest/what-if`

## 环境变量

复制模板：

```bash
cp .env.example .env
```

本地最小配置：

```env
LLM_PROVIDER=ark
ARK_API_KEY=你的字节Ark API Key
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=doubao-seed-1-6-flash-250828
ARK_FALLBACK_MODELS=doubao-seed-1-6-flash-250828
CORS_ALLOW_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
ZHIHU_ACCESS_SECRET=你的知乎开放平台 Access Secret
ZHIHU_SEARCH_URL=https://developer.zhihu.com/api/v1/content/zhihu_search
```

## 本地运行

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

## Render 部署

仓库根目录已经提供 `render.yaml`，推荐使用 Render Blueprint。

部署后需要在 Render Environment 中配置：

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

部署完成后，把 Render 后端域名填到 Vercel 前端环境变量：

```env
VITE_API_BASE_URL=https://你的-render-service.onrender.com
```
