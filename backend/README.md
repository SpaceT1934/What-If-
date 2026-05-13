# Backend

FastAPI 后端服务，负责游客模式下的系统推演、人生星尘生成、What If 平行宇宙推演，以及知乎开放平台搜索结果接入。

## 接口

- `GET /health`
- `GET /api/debug/llm-auth`
- `POST /api/guest/analyze`
- `POST /api/guest/generate-stardust`
- `POST /api/guest/what-if`

## 本地运行

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

## CloudBase 云托管部署

后端部署请使用仓库根目录的 `Dockerfile`，不要只上传 `backend/` 目录。原因是后端会读取根目录：

```text
mock-data/test_data.md
```

CloudBase 云托管配置：

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
CORS_ALLOW_ORIGINS=https://你的前端域名,http://localhost:5173,http://127.0.0.1:5173
```

部署后检查：

```text
https://你的-cloudbase-后端域名/health
```
