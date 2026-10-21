# 卓文的个人订阅站

固定订阅路径：`clash.yaml`（Clash Verge Rev / Meta）与 `shadowrocket.txt`（Shadowrocket）。
每日北京时间 03:15、09:15、15:15、21:15 从公开来源收集节点，去重，经 Mihomo 测活后发布；任务失败、两种输出为空或不一致时不部署，线上保留上一次成功版本。没有下载速度保证，云端检测不代表设备所在网络可达。

## 首次部署

1. 在 GitHub 创建公开仓库 `personal-vpn`，默认分支 `main`。将本项目所有文件上传，包括 `.github/workflows/update.yml`。
2. 仓库 Settings → Pages → Source 选择 **GitHub Actions**。
3. Actions → Daily subscription update → Run workflow。
4. 等待 build 和 deploy 都成功，在部署结果中打开站点，复制订阅地址。首轮必须有真实节点通过才能发布；不存在预填的“可用”节点。
5. 在客户端导入并开启自动更新，使用当前网络重新测速。

也可在本地解压项目后执行：
```
gh auth login
gh repo create personal-vpn --public --source . --push
```
执行前须 `git init -b main`、`git add .`、`git commit -m "Initial subscription station"`。
没有自购服务器或域名配置，不需要任何付费密钥。只使用标准 ubuntu-latest runner。公共仓库中的配置和发布文件公开，请勿写入私人订阅或自有节点密码。

## 本地检查

Python 3.11+：
```
python -m pip install .
python -m unittest discover -s tests
python scripts/install_mihomo.py --output .bin/mihomo
ALIYUN_FC_ENABLED=0 MAX_NODES=300 MAX_OUTPUT_NODES=40 subbench run --output .staging
python scripts/publish.py .staging public .bin/mihomo
```

来源维护在 config/sources.txt。默认最多检测 1,200 个候选，按来源和协议轮流取样；要求连续两次检测通过，再从不同服务器中选择最多 120 个进行三轮 HTTPS 检测，每轮间隔 20 秒。检查 Google 204、Cloudflare trace 和 ChatGPT 首页；挑战页、限制页、超时均不通过。最多发布 30 个，未验证登录后的 ChatGPT 对话。两种格式只收录同时可导出的节点。云端任务最多 25 分钟；任一步骤失败都不会进入部署。

客户端 MATCH 规则默认将流量交给 PROXY；可在客户端选择 DIRECT，或自行配置分流。小火箭订阅仅同步节点，不同步 Clash 策略。

## 运维

首页显示真实生成时间；超过 48 小时提示过期。构建失败原因查看 Actions，失败不会改写首页，因此旧首页的日期是判断依据。定时任务可能延迟或因长期无活动而停用，需定期检查。首次部署前先启用 Pages；若部署报 environment/Pages 错误，检查仓库 Settings → Pages。

基于 MIT 开源项目改造，来源及快照见 UPSTREAM.md，保留 LICENSE。
