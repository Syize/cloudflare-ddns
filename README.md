# Cloudflare DDNS

这个脚本通过 Python 解析机器的 IP 地址并更新至 Cloudflare.

## 使用方法

你需要申请 Cloudflare 的 API 令牌并设置环境变量 `CLOUDFLARE_EMAIL` 和 `CLOUDFLARE_KEY`

```bash
env CLOUDFLARE_EMAIL="Your Email" CLOUDFLARE_KEY="Your API token" python main.py
```