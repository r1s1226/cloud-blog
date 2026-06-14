# 📸 실습 스크린샷 캡처 가이드 / 截图采集清单

博客里每个带虚线框的 `📸` 都是要放**你自己实操截图**的地方。这台电脑跑不了容器(虚拟化被禁),所以用**免费浏览器 playground** 来跑同样的命令、截真图。截好发我,我帮你接进对应位置。

> 难度标注:**[易]** = 复制粘贴即可,几十秒出图;**[选]** = 较重/需搭环境,有空再做,不做也行。优先把 **[易]** 的截全就够撑住"实际做了练习"。

---

## 0. 两个 playground 怎么启动

### 🐳 Google Cloud Shell — 用于 Docker 周(week04~06)
> ⚠️ Play with Docker 已于 2026-03-01 停用,改用 Google Cloud Shell(Docker 预装、免费)。
1. 打开 **https://shell.cloud.google.com**,用 **Google 账号**登录(首次点 Continue / 启动 Cloud Shell)。
2. 出现浏览器终端后 `docker` 已就绪,命令直接粘进去。截图就截这个终端区域。
3. 需要"网页访问"截图时(下面 week04 的 `localhost:8080`):点终端窗口右上的 **Web Preview(网页预览)→ Change port → 8080**,打开的页面就是容器响应 → 截那个页面。

> 替代 환경(任选其一也行):**GitHub Codespaces**(你已有 GitHub:仓库页 Code → Codespaces → Create,终端里有 docker)、**killercoda Ubuntu playground**(需先 `curl -fsSL https://get.docker.com | sh`)。

### ☸️ killercoda — 用于 Kubernetes 周(week07、09~14)
1. 打开 **https://killercoda.com**
2. 右上 **Login**(用 GitHub 账号最快)
3. 打开 K8s 游乐场:**https://killercoda.com/playgrounds/scenario/kubernetes**
4. 等十几秒,出现 `controlplane $` 终端,`kubectl` 已就绪、集群已建好。命令粘进去即可。

> 两个 playground 里很多实操要用课程示例文件,先 `git clone` 一次即可(下面每周有写)。

---

## 1. AWS 周(week01~03)— playground 跑不了
AWS 需要你自己的账号+免费套餐,playground 没有。这三周的截图二选一:
- 有 AWS 账号:登录控制台,按博客步骤截图(EC2 实例列表、VPC、安全组等)。
- 没有/不想注册:这三周保持文字版即可(已写明步骤),不强求控制台截图。

---

## 2. Docker 周 — 在 Google Cloud Shell 里跑

### week04 — 도커 기초
```bash
# [易] 📸 "docker version 출력"
docker version

# [易] 📸 "container ls / logs 출력"
docker run -d --name web -p 8080:80 diamol/ch03-web-ping
docker container ls
docker container logs web

# [易] 📸 "localhost:8080 접속 화면"
#     위에서 -p 8080:80 으로 띄운 뒤, Cloud Shell 우상단 [Web Preview → port 8080] 클릭 → 열린 페이지 캡처

# [易] 📸 "image build / image ls 출력"
git clone https://github.com/sixeyed/diamol.git
cd diamol/ch03/exercises/web-ping
docker image build -t web-ping .
docker image ls 'w*'

# [易] 📸 "이미지 크기 비교"  (멀티 스테이지)
cd ~/diamol/ch04/exercises/image-of-the-day
docker image build -t iotd .
docker image ls | grep -E 'iotd|maven'   # 빌더(maven) vs 최종 이미지 크기 비교
```

### week05 — 레지스트리·볼륨·컴포즈
```bash
# [易] 📸 "docker-compose up 실행 화면"
cd ~/diamol/ch07/exercises/image-of-the-day
docker compose up -d
docker compose ps

# [易] 📸 "nslookup 다중 IP 결과"  (컨테이너 간 DNS)
docker compose up -d --scale image-of-the-day=2
docker exec -it $(docker ps -qf name=image-gallery) sh -c "nslookup image-of-the-day" 2>/dev/null || \
docker run --rm --network container:$(docker ps -qf name=image-gallery) busybox nslookup image-of-the-day

# [易] 📸 "볼륨 데이터 유지 확인"
docker volume create todo-list
docker run -d -p 8090:80 -v todo-list:/data --name t1 diamol/ch06-todo-list
docker rm -f t1
docker run -d -p 8091:80 -v todo-list:/data --name t2 diamol/ch06-todo-list   # 같은 볼륨 → 데이터 유지
docker volume ls

# [选] 📸 "docker login / push 결과"   (Docker Hub에 푸시; 본인 계정명으로)
docker login
docker tag diamol/ch06-todo-list <당신ID>/todo-list:v1
docker push <당신ID>/todo-list:v1

# [选] 📸 "사설 레지스트리 push 결과"
docker run -d -p 5000:5000 --restart always --name registry registry:2
docker tag diamol/ch06-todo-list localhost:5000/todo:v1
docker push localhost:5000/todo:v1
```

### week06 — 헬스체크·CI
```bash
# [易] 📸 "네 번째 curl 실패 + 컨테이너는 여전히 Up"
docker run -d -p 8080:80 --name api diamol/ch08-numbers-api
curl http://localhost:8080/rng; echo
curl http://localhost:8080/rng; echo
curl http://localhost:8080/rng; echo
curl http://localhost:8080/rng; echo   # 4번째부터 실패
docker container ls                    # 그래도 STATUS는 Up

# [选] 📸 "container inspect의 unhealthy 상태"  (HEALTHCHECK 이미지 v2 빌드 필요 → 시간 있을 때)
# [选] 📸 "docker-compose config 병합 결과"
cd ~/diamol/ch10/exercises   # (없으면 ch08/ch11 등 compose 예제 디렉터리)
docker compose -f docker-compose.yml -f docker-compose-v2.yml config 2>/dev/null | head -40

# [选] 📸 "Gogs(localhost:3000)와 Jenkins 빌드 로그"  / "레지스트리 API 응답"
#     → Gogs+Jenkins 스택은 무겁다. 시간 없으면 생략.
```

---

## 3. Kubernetes 周 — 在 killercoda 里跑

먼저 한 번만 클론:
```bash
git clone https://github.com/sixeyed/kiamol.git
```

### week07 — 클러스터
> kubeadm 멀티노드 구축(containerd·Calico·join)은 playground에서 **재현 불가**(이미 만들어진 클러스터라). 아래 하나만:
```bash
# [易] 📸 "kubectl get nodes 결과(Ready)"
kubectl get nodes
```
나머지 kubeadm 관련 3개 📸(containerd / init join / Calico)는 **생략 또는 보류**(환경 종속 단계).

### week09 — 파드·디플로이먼트·서비스
```bash
cd ~/kiamol/ch02
# [易] 📸 "kubectl get pods 출력"
kubectl run hello-kiamol --image=kiamol/ch02-hello-kiamol
kubectl wait --for=condition=Ready pod hello-kiamol
kubectl get pods

# [易] 📸 "레이블 수정으로 파드가 추가된 화면"
kubectl create deployment hello-kiamol-2 --image=kiamol/ch02-hello-kiamol
kubectl label pods -l app=hello-kiamol-2 --overwrite app=hello-kiamol-x
kubectl get pods -o custom-columns=NAME:metadata.name,LABELS:metadata.labels

# [易] 📸 "Go 버튼 정상 동작 화면" → 어렵다면 대신 서비스 통신 확인으로 대체
cd ~/kiamol/ch03
kubectl apply -f numbers/api.yaml -f numbers/web.yaml
kubectl apply -f numbers/api-service.yaml 2>/dev/null
kubectl get svc

# [选] 📸 "LoadBalancer EXTERNAL-IP" / "port-forward 후 브라우저 화면" / "nslookup 결과"
kubectl exec deploy/sleep -- sh -c 'nslookup numbers-api' 2>/dev/null
```

### week10 — 컨피그맵·볼륨·스케일링
```bash
cd ~/kiamol/ch04
# [易] 📸 "printenv 결과"
kubectl create configmap sleep-config-literal --from-literal=kiamol.section='4.1'
kubectl describe cm sleep-config-literal
kubectl apply -f sleep/sleep.yaml
kubectl exec deploy/sleep -- sh -c 'printenv | grep "^KIAMOL"' 2>/dev/null

cd ~/kiamol/ch05
# [易] 📸 "kubectl get pv / pvc (Bound·Pending)"
kubectl apply -f todo-list/persistentVolume.yaml
kubectl apply -f todo-list/postgres-persistentVolumeClaim.yaml
kubectl get pv,pvc

cd ~/kiamol/ch06
# [易] 📸 "로드밸런싱 응답"
kubectl apply -f whoami/
kubectl apply -f whoami/update/whoami-replicas-3.yaml
kubectl get pods -l app=whoami-web
# [选] 📸 "kubectl get ds"
kubectl apply -f pi/proxy/daemonset/nginx-ds.yaml
kubectl get ds
```

### week11 — 멀티컨테이너·스테이트풀셋·롤아웃
```bash
cd ~/kiamol/ch08
# [易] 📸 "get statefulset / 규칙적 파드 이름"
kubectl apply -f todo-list/db/
kubectl get statefulset
kubectl get pods -l app=todo-db

cd ~/kiamol/ch09
# [易] 📸 "rollout history"
kubectl apply -f vweb/
kubectl set image deployment/vweb web=kiamol/ch09-vweb:v2
kubectl rollout history deploy/vweb
```

### week12 — 헬름·프로브
```bash
# 헬름 설치(killercoda에 없으면)
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
# [易] 📸 "helm search repo 결과" / "helm install / helm ls 결과"
helm repo add kiamol https://kiamol.net
helm repo update
helm search repo vweb --versions
helm install --set servicePort=8010 --set replicaCount=1 ch10-vweb kiamol/vweb --version 1.0.0
helm ls

cd ~/kiamol/ch12
# [选] 📸 "get endpoints — 레디니스로 제외" / "리브니스로 파드 재시작" / "helm test 통과"
```

### week13 — 로깅·모니터링·인그레스  [大多为 选]
> Fluent Bit / Elasticsearch / Kibana / Prometheus / Grafana 是重型栈,UI 还要端口转发,playground 里较麻烦。**时间紧就整周保持文字版**,或只截一张:
```bash
cd ~/kiamol/ch13
# [选] 📸 "여러 파드 로그가 통합된 화면"
kubectl apply -f fluentbit/ 2>/dev/null
kubectl get pods -A | head
```

### week14 — RBAC·스케줄링·HPA·CRD
```bash
# [易] 📸 "describe clusterrole cluster-admin 결과"
kubectl describe clusterrole cluster-admin | head -30

# [易] 📸 "auth can-i 결과"
kubectl auth can-i '*' '*'
kubectl auth can-i get pods --as system:serviceaccount:default:default

# [易] 📸 "taint 후 Pending 상태"
kubectl taint nodes --all demo=x:NoSchedule
kubectl run t --image=nginx
kubectl get pods           # t 가 Pending
kubectl taint nodes --all demo=x:NoSchedule-   # 원복

cd ~/kiamol/ch20 2>/dev/null
# [选] 📸 "get todos / 커스텀 컨트롤러 로그" / "get nats / get mysql"  (CRD/오퍼레이터, 시간 있을 때)
```

---

## 4. 截好图后怎么办
1. 截图保存成 PNG。
2. 文件名建议跟 📸 对应,例如 `week04-docker-version.png`、`week09-get-pods.png`。
3. 全部丢进 `assets/img/` 文件夹。
4. 告诉我「这张图对应第几周哪个 📸」,我把对应的 `!!! capture "..."` 占位框换成你的图片并重新构建。
   (或者你自己照 README 的方法:把 capture 框换成 `![설명](../assets/img/문件名.png)` 再 `python build.py`)

> 建议至少把 week04、week09、week10、week14 的 **[易]** 全截到——这几周覆盖 Docker + K8s 核心,足以证明"실제 실습 수행".
