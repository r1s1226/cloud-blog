# -*- coding: utf-8 -*-
"""
정적 블로그 빌더.
_content/*.md  ->  posts/*.html  +  index.html
마크다운 + 코드 하이라이트(pygments) + admonition(콜아웃) 지원.
"""
import os, re, markdown
from pygments.formatters import HtmlFormatter

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "_content")
POSTS_DIR = os.path.join(ROOT, "posts")
ASSETS = os.path.join(ROOT, "assets")

SITE_TITLE = "Cloud Programming Lab"
SITE_SUBTITLE = "클라우드 프로그래밍 학습 기록 — AWS · Docker · Kubernetes"

# 게시물 메타데이터 (순서 = 사이트 순서)
POSTS = [
    dict(slug="week01", week="01", group="클라우드 기초 · AWS",
         title="클라우드란? — 개념, AWS 입문, 리눅스 가상머신",
         summary="온프레미스 vs 클라우드, IaaS·PaaS·SaaS, 퍼블릭/프라이빗/하이브리드, 가상화·서버리스. AWS 가입과 VMware로 우분투 설치, 리눅스 기초 명령어까지.",
         tags=["클라우드", "IaaS/PaaS/SaaS", "AWS", "가상화", "Linux", "VMware"]),
    dict(slug="week02", week="02", group="클라우드 기초 · AWS",
         title="AWS 컴퓨팅 — 서버 기초와 Amazon EC2",
         summary="서버/웹서버/DB서버 개념, 리눅스 vs 윈도우 서버, EC2 인스턴스 유형·AMI·EBS·보안 그룹·키 페어. EC2 인스턴스를 배포하고 SSH로 접속하는 실습.",
         tags=["AWS", "EC2", "AMI", "EBS", "보안 그룹", "SSH"]),
    dict(slug="week03", week="03", group="클라우드 기초 · AWS",
         title="네트워크 기초와 Amazon VPC",
         summary="OSI 7계층, IP/서브넷/CIDR, TCP·UDP·포트. AWS 네트워킹과 VPC로 퍼블릭/프라이빗 서브넷 구성, 인터넷 게이트웨이·NAT·보안 그룹·NACL.",
         tags=["네트워크", "VPC", "서브넷", "CIDR", "보안 그룹", "NACL"]),
    dict(slug="week04", week="04", group="Docker",
         title="도커 개념과 이미지 빌드 — 멀티 스테이지까지",
         summary="컨테이너 vs VM, 도커 설치, 컨테이너 실행/웹 호스팅, Dockerfile 작성과 레이어 캐시 최적화, 멀티 스테이지 빌드로 Java·Node.js·Go 이미지 경량화.",
         tags=["Docker", "컨테이너", "Dockerfile", "멀티 스테이지", "이미지 레이어"]),
    dict(slug="week05", week="05", group="Docker",
         title="도커 레지스트리 · 볼륨 · 컴포즈",
         summary="Docker Hub 푸시와 사설 레지스트리, 이미지 태그 전략과 골든 이미지, 볼륨/바인드 마운트로 데이터 영속화, 도커 컴포즈로 다중 컨테이너 앱 실행.",
         tags=["Docker", "Registry", "Volume", "Docker Compose", "골든 이미지"]),
    dict(slug="week06", week="06", group="Docker",
         title="헬스 체크 · 다중 환경 컴포즈 · CI",
         summary="HEALTHCHECK와 디펜던시 체크로 복원력 있는 컨테이너 만들기, 오버라이드 파일로 환경별 구성, Gogs+Jenkins로 도커 기반 CI 파이프라인 구축.",
         tags=["Docker", "HEALTHCHECK", "Compose Override", "CI", "Jenkins"]),
    dict(slug="week07", week="07", group="Kubernetes 입문",
         title="쿠버네티스 기본 구조와 클러스터 구축",
         summary="쿠버네티스 개념(클러스터/노드/파드), kubeadm으로 마스터·워커 노드 구성과 Calico CNI, 그리고 Rancher Desktop·K3s·EKS·AKS 등 다양한 실습 환경.",
         tags=["Kubernetes", "kubeadm", "CNI", "K3s", "EKS/AKS"]),
    dict(slug="week09", week="09", group="Kubernetes 입문",
         title="파드 · 디플로이먼트 · 서비스(네트워크)",
         summary="파드와 컨트롤러 객체, 디플로이먼트로 자가치유·스케일링, 매니페스트(YAML) 선언적 배포, ClusterIP·LoadBalancer·NodePort·ExternalName 서비스로 트래픽 라우팅.",
         tags=["Kubernetes", "Pod", "Deployment", "Service", "kubectl"]),
    dict(slug="week10", week="10", group="Kubernetes 입문",
         title="컨피그맵 · 볼륨/퍼시스턴시 · 스케일링",
         summary="컨피그맵/비밀값으로 설정 주입, emptyDir·hostPath·PV/PVC로 데이터 영속화, 레플리카셋·디플로이먼트·데몬셋으로 스케일링과 고가용성 확보.",
         tags=["Kubernetes", "ConfigMap", "PV/PVC", "ReplicaSet", "DaemonSet"]),
    dict(slug="week11", week="11", group="Kubernetes 심화",
         title="멀티컨테이너 파드 · 스테이트풀셋 · 롤아웃/롤백",
         summary="사이드카·초기화 컨테이너 패턴, 스테이트풀셋과 헤드리스 서비스·볼륨 클레임 템플릿, 롤링 업데이트와 롤백, Recreate vs RollingUpdate 전략.",
         tags=["Kubernetes", "사이드카", "StatefulSet", "롤아웃", "롤백"]),
    dict(slug="week12", week="12", group="Kubernetes 심화",
         title="헬름 · 개발 워크플로(CI/CD) · 자기수복 앱",
         summary="헬름 차트로 패키징과 의존 관계 모델링, 도커/쿠버네티스 개발 워크플로와 컨텍스트·네임스페이스, 레디니스·리브니스 프로브로 자기수복형 애플리케이션 구성.",
         tags=["Kubernetes", "Helm", "CI/CD", "Probe", "Namespace"]),
    dict(slug="week13", week="13", group="Kubernetes 운영",
         title="중앙 로그 관리 · 모니터링 · 인그레스",
         summary="Fluent Bit+Elasticsearch+Kibana 로그 파이프라인, Prometheus+Grafana 모니터링과 익스포터, Ingress 컨트롤러로 호스트/경로 기반 트래픽 라우팅.",
         tags=["Kubernetes", "Fluentd", "Prometheus", "Grafana", "Ingress"]),
    dict(slug="week14", week="14", group="Kubernetes 운영",
         title="RBAC 보안 · 스케줄링/HPA · CRD·오퍼레이터",
         summary="RBAC(Role/Binding/ServiceAccount)로 권한 제어, 테인트·어피니티 스케줄링과 HPA 자동 스케일링, CRD와 커스텀 컨트롤러·오퍼레이터로 쿠버네티스 확장.",
         tags=["Kubernetes", "RBAC", "스케줄링", "HPA", "CRD/Operator"]),
]

MD_EXT = ["extra", "codehilite", "admonition", "toc", "sane_lists", "nl2br"]
MD_CFG = {
    "codehilite": {"guess_lang": False, "css_class": "highlight"},
    "toc": {"permalink": False},
}

def md_to_html(text):
    md = markdown.Markdown(extensions=MD_EXT, extension_configs=MD_CFG)
    body = md.convert(text)
    toc = getattr(md, "toc", "")
    return body, toc

def head(title, depth):
    """depth: 0 = repo root (index), 1 = posts/ 하위"""
    prefix = "../" if depth == 1 else ""
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="{prefix}assets/css/style.css">
</head>
<body>
<header class="topbar">
  <div class="wrap topbar-inner">
    <a class="brand" href="{prefix}index.html">☁ {SITE_TITLE}</a>
    <nav class="topnav">
      <a href="{prefix}index.html">홈</a>
      <a href="{prefix}index.html#posts">강의별 기록</a>
      <a href="{prefix}index.html#about">소개</a>
    </nav>
  </div>
</header>
<main class="wrap">
"""

FOOT = """</main>
<footer class="site-footer">
  <div class="wrap">
    <p>클라우드 프로그래밍 기말 과제 · 개인 학습 포트폴리오</p>
    <p class="muted">AWS · Docker · Kubernetes 실습 기록</p>
  </div>
</footer>
</body>
</html>"""

def render_index():
    intro_path = os.path.join(CONTENT, "index.md")
    intro_html = ""
    if os.path.exists(intro_path):
        with open(intro_path, encoding="utf-8") as f:
            intro_html, _ = md_to_html(f.read())

    # 그룹별 카드
    groups = []
    seen = []
    for p in POSTS:
        if p["group"] not in seen:
            seen.append(p["group"])
    cards_by_group = {g: [] for g in seen}
    for p in POSTS:
        tags = "".join(f'<span class="tag">{t}</span>' for t in p["tags"])
        card = f"""<a class="card" href="posts/{p['slug']}.html">
  <div class="card-top"><span class="weekbadge">WEEK {p['week']}</span></div>
  <h3>{p['title']}</h3>
  <p class="card-sum">{p['summary']}</p>
  <div class="tags">{tags}</div>
</a>"""
        cards_by_group[p["group"]].append(card)

    sections = []
    for g in seen:
        cards = "\n".join(cards_by_group[g])
        sections.append(f"""<section class="group">
  <h2 class="group-title">{g}</h2>
  <div class="card-grid">
  {cards}
  </div>
</section>""")
    groups_html = "\n".join(sections)

    html = head(f"{SITE_TITLE} — {SITE_SUBTITLE}", 0)
    html += f"""<section class="hero">
  <p class="hero-kicker">CLOUD PROGRAMMING · 학습 포트폴리오</p>
  <h1 class="hero-title">{SITE_SUBTITLE}</h1>
  <div class="hero-intro">{intro_html}</div>
  <div class="stackbadges">
    <span class="sb sb-aws">AWS</span>
    <span class="sb sb-docker">Docker</span>
    <span class="sb sb-k8s">Kubernetes</span>
    <span class="sb sb-helm">Helm</span>
    <span class="sb sb-linux">Linux</span>
    <span class="sb sb-prom">Prometheus</span>
  </div>
</section>
<div id="posts"></div>
{groups_html}
"""
    html += FOOT
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def render_post(idx, p):
    src = os.path.join(CONTENT, p["slug"] + ".md")
    with open(src, encoding="utf-8") as f:
        body, toc = md_to_html(f.read())

    prev_p = POSTS[idx - 1] if idx > 0 else None
    next_p = POSTS[idx + 1] if idx < len(POSTS) - 1 else None
    prev_html = (f'<a class="pn prev" href="{prev_p["slug"]}.html">← WEEK {prev_p["week"]}<span>{prev_p["title"]}</span></a>'
                 if prev_p else '<span class="pn disabled"></span>')
    next_html = (f'<a class="pn next" href="{next_p["slug"]}.html">WEEK {next_p["week"]} →<span>{next_p["title"]}</span></a>'
                 if next_p else '<span class="pn disabled"></span>')

    tags = "".join(f'<span class="tag">{t}</span>' for t in p["tags"])
    toc_block = f'<aside class="toc"><div class="toc-title">목차</div>{toc}</aside>' if toc.strip() else ""

    html = head(f"WEEK {p['week']} · {p['title']} — {SITE_TITLE}", 1)
    html += f"""<article class="post">
  <div class="post-head">
    <span class="weekbadge">WEEK {p['week']}</span>
    <span class="post-group">{p['group']}</span>
    <h1>{p['title']}</h1>
    <div class="tags">{tags}</div>
  </div>
  <div class="post-layout">
    <div class="post-body">
    {body}
    </div>
    {toc_block}
  </div>
  <nav class="postnav">
    {prev_html}
    {next_html}
  </nav>
</article>
"""
    html += FOOT
    with open(os.path.join(POSTS_DIR, p["slug"] + ".html"), "w", encoding="utf-8") as f:
        f.write(html)

def write_pygments_css():
    css = HtmlFormatter(style="friendly").get_style_defs(".highlight")
    with open(os.path.join(ASSETS, "css", "pygments.css"), "w", encoding="utf-8") as f:
        f.write(css)

def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "css"), exist_ok=True)
    write_pygments_css()
    render_index()
    built = 0
    for i, p in enumerate(POSTS):
        if os.path.exists(os.path.join(CONTENT, p["slug"] + ".md")):
            render_post(i, p)
            built += 1
        else:
            print("SKIP (no content yet):", p["slug"])
    print(f"Built index + {built}/{len(POSTS)} posts.")

if __name__ == "__main__":
    main()
