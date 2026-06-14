# 클라우드 프로그래밍 학습 포트폴리오 (Cloud Programming Lab)

AWS · Docker · Kubernetes 한 학기 수업 내용과 실습 과정을 주차별로 정리한 정적 블로그.
GitHub Pages 로 호스팅하는 순수 HTML/CSS 사이트(빌드 도구·서버 불필요).

---

## 📂 文件结构 / Structure

```
cloud-blog/
├─ index.html          # 首页(自动生成)
├─ posts/week*.html    # 各周文章(自动生成)
├─ assets/css/         # 样式 (style.css + pygments.css)
├─ _content/*.md       # ★源文件:你只需要编辑这里的 Markdown
├─ build.py            # 构建脚本:Markdown → HTML
├─ .nojekyll           # 告诉 GitHub Pages 按静态文件原样serve
└─ README.md
```

> 编辑只改 `_content/*.md`,然后跑 `python build.py` 重新生成 HTML。

---

## 🖥️ 本地预览 / Local preview

```bash
cd cloud-blog
python -m http.server 8099
# 浏览器打开 http://localhost:8099
```

## 🔧 重新构建 / Rebuild

改完 `_content/` 里的 Markdown 后:

```bash
pip install markdown pygments      # 仅首次
python build.py
```

---

## 📸 加入自己的实습 截图(强烈建议)

文章里有很多带虚线框的 `📸` 占位提示(`!!! capture`),那是建议你放**自己实습截图**的地方。
评分会看「실제 실습 수행 여부(是否真的做了实습)」,所以放上真实截图能明显加分。

1. 把截图放进 `assets/img/` (예: `assets/img/ec2-console.png`)。
2. `_content/weekXX.md` 里把对应的 capture 콜아웃替换成图片,例如:

   ```markdown
   ![EC2 인스턴스 시작 화면](../assets/img/ec2-console.png)
   ```
3. `python build.py` 重新构建。

---

## 🚀 部署到 GitHub Pages

```bash
cd cloud-blog
git init
git add .
git commit -m "클라우드 프로그래밍 학습 포트폴리오"
git branch -M main
# 在 GitHub 上新建一个仓库(例如 cloud-blog),然后:
git remote add origin https://github.com/<당신의-아이디>/cloud-blog.git
git push -u origin main
```

그다음 GitHub 仓库 → **Settings → Pages** → *Build and deployment* →
Source: **Deploy from a branch**, Branch: **main / (root)** → Save.

1~2분 뒤 公开 URL:
`https://<당신의-아이디>.github.io/cloud-blog/`

> 제출 시 이 URL 이 **외부에서 접속 가능한지(공개 설정)** 꼭 확인할 것.
