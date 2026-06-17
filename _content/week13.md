쿠버네티스 운영 주차. 중앙 로그(Fluent Bit·Elasticsearch·Kibana) → 모니터링(Prometheus·Grafana·익스포터) → 인그레스(Nginx Ingress) 순서로 실습한다.

## 중앙 로그 — Fluent Bit + Elasticsearch

컨테이너 로그는 각 노드 `/var/log/containers/`에 파일로 쌓인다. Fluent Bit이 노드마다 데몬셋으로 떠서 이 경로를 hostPath로 마운트해 수집한다.

```bash
kubectl apply -f timecheck/                                            # 로그 생성용 앱 배치
kubectl logs -l app=timecheck --all-containers -n kiamol-ch13-dev --tail 1  # 표준 도구 로그 확인

# 노드 로그 디렉터리 직접 확인
kubectl exec -it deploy/sleep -- sh
cd /var/log/containers/
ls timecheck*kiamol-ch13*_logger*
cat $(ls timecheck*kiamol-ch13-dev_logger*) | tail -n 1
exit
```

Fluent Bit 파이프라인: `[INPUT]`이 파일을 읽고 `[FILTER]`가 쿠버네티스 메타데이터를 붙이며 `[OUTPUT]`이 내보낸다.

```yaml
[INPUT]
    Name                tail                                   # 파일 끝부터 읽음
    Tag                 kube.*                                 # 수집 로그 태그 접두어
    Path                /var/log/containers/timecheck*.log
    Parser              docker                                 # JSON 컨테이너 로그 파서
    Refresh_Interval    10                                     # 파일 목록 확인 간격
[OUTPUT]
    Name                stdout                                 # 표준 출력으로
    Format              json_lines                             # 한 엔트리를 한 줄로
    Match               kube.*                                 # kube로 시작하는 태그만
```

```bash
kubectl apply -f fluentbit/                                            # 데몬셋·컨피그맵 배치
kubectl logs -l app=fluent-bit -n kiamol-ch13-logging --tail 2         # 수집 로그 확인
kubectl apply -f fluentbit/update/fluentbit-config-match.yaml          # 쿠버네티스 필터 적용
kubectl rollout restart ds/fluent-bit -n kiamol-ch13-logging           # 데몬셋 재시작
```

!!! capture "여러 파드 로그가 통합된 화면"
    (실습 화면 캡처)

### Elasticsearch + Kibana

`[OUTPUT]`을 `es` 플러그인으로 바꾸면 지정 인덱스에 로그가 저장되고, Kibana가 조회 프런트엔드를 맡는다.

```yaml
[OUTPUT]
    Name      es                          # 테스트 네임스페이스 로그를
    Match     kube.kiamol-ch13-test.*     # Elasticsearch에 저장
    Host      elasticsearch
    Index     test                        # 인덱스 이름
```

```bash
kubectl apply -f elasticsearch/                                        # Elasticsearch 배치
kubectl apply -f kibana/                                               # Kibana 배치
kubectl get svc kibana -o jsonpath='http://{.status.loadBalancer.ingress[0].*}:5601' -n kiamol-ch13-logging  # 접속 URL
kubectl apply -f fluentbit/update/fluentbit-config-elasticsearch.yaml  # es 출력으로 변경
kubectl rollout restart ds/fluent-bit -n kiamol-ch13-logging           # 재시작
```

Kibana에서 인덱스 패턴 생성 순서: Discover → Create index pattern → `test` 입력 → Time Filter field `@timestamp` 선택 → Create → Discover에서 로그 확인.

!!! capture "Kibana Discover 로그 조회 화면"
    (실습 화면 캡처)

## 모니터링 — Prometheus + Grafana

Prometheus는 대상에서 메트릭을 가져오는 풀링 방식이며, 쿠버네티스 API로 대상을 자동 발견해 스크래핑한다.

`scrape_configs`의 `kubernetes_sd_configs`로 파드를 발견하고 `relabel_configs`로 대상을 걸러낸다.

```yaml
scrape_configs:
  - job_name: 'test-pods'
    kubernetes_sd_configs:            # 쿠버네티스 API로 대상 발견
    - role: pod
    relabel_configs:
    - source_labels:
      - __meta_kubernetes_namespace
      action: keep                    # 테스트 네임스페이스 파드만
      regex: kiamol-ch14-test
```

```bash
kubectl apply -f prometheus/                                  # Prometheus 배치 (:9090 /targets·/graph)
kubectl apply -f timecheck/                                   # 스크래핑 대상 앱 배치
kubectl scale deploy/timecheck --replicas 2 -n kiamol-ch14-test  # 인스턴스별 메트릭 생산
```

!!! capture "Prometheus /targets·/graph 화면"
    (실습 화면 캡처)

파드 애너테이션으로 스크래핑 동작을 제어한다: `prometheus.io/scrape: "false"`(제외), `prometheus.io/path`(경로), `prometheus.io/port`(포트).

### Grafana

Grafana는 Prometheus를 데이터 소스로 대시보드를 그리며, 대시보드 정의를 컨피그맵으로 배치한다.

```bash
kubectl apply -f grafana/        # Grafana 배치 (:3000, kiamol/kiamol)
.\loadgen.ps1                    # 부하 생성 (윈도우)
# chmod +x ./loadgen.sh && ./loadgen.sh   # (리눅스/macOS)
```

### 익스포터

Prometheus 형식 메트릭을 못 내는 앱은 익스포터를 사이드카로 같은 파드에 넣어 `localhost`로 본체 상태를 읽고 별도 포트로 메트릭을 노출한다.

```yaml
template:
  metadata:
    labels:
      app: todo-proxy
    annotations:
      prometheus.io/port: "9113"               # 익스포터 엔드포인트 포트
  spec:
    containers:
      - name: nginx
        # ... nginx 컨테이너 정의는 그대로
      - name: exporter                          # 익스포터 사이드카
        image: nginx/nginx-prometheus-exporter:0.8.0
        ports:
          - name: metrics
            containerPort: 9113
        args:                                   # nginx 상태 페이지에서 추출
          - -nginx.scrape-uri=http://localhost/stub_status
```

```bash
kubectl apply -f todo-list/update/proxy-with-exporter.yaml             # 익스포터 사이드카 추가
kubectl logs -l app=todo-proxy -n kiamol-ch14-test -c exporter         # 익스포터 로그 확인
kubectl rollout restart deploy grafana -n kiamol-ch14-monitoring       # Grafana 재시작
```

!!! capture "Grafana 대시보드"
    (실습 화면 캡처)

## 인그레스 — Nginx Ingress

인그레스는 도메인·경로 규칙으로 요청을 백엔드 서비스에 매핑해 하나의 공인 IP로 클러스터 전체를 라우팅한다. 규칙을 집행하는 리버스 프록시가 인그레스 컨트롤러다.

```bash
kubectl apply -f hello-kiamol/                                 # ClusterIP 내부 전용 배치
kubectl port-forward svc/hello-kiamol 8015:80                  # 내부 접근만 가능함을 확인

kubectl -n kube-system delete helmcharts.helm.cattle.io traefik  # (K3s) 기본 Traefik 제거
kubectl apply -f ingress-nginx/                                # Nginx 인그레스 컨트롤러 배치

kubectl apply -f hello-kiamol/ingress/localhost.yaml           # 라우팅 규칙 배치
kubectl get ingress
```

호스트·경로 규칙. 호스트를 지정하면 그 도메인 요청에만 적용된다.

```yaml
spec:
  rules:
  - host: hello.kiamol.local        # 이 도메인 요청에만 적용
    http:
      paths:
      - path: /                     # 해당 도메인 모든 요청을
        backend:                    # hello-kiamol 서비스가 처리
          serviceName: hello-kiamol
          servicePort: 80
```

```bash
./add-to-hosts.ps1 hello.kiamol.local ingress-nginx           # hosts 파일에 도메인 추가 (관리자 권한)
kubectl apply -f hello-kiamol/ingress/hello.kiamol.local.yaml
kubectl get ingress
```

!!! capture "도메인 접속 결과 (hello.kiamol.local)"
    (실습 화면 캡처)

### 경로 라우팅

같은 도메인에서 경로로 앱을 나눈다. `pathType`은 전방 일치 `Prefix`, 완전 일치 `Exact`.

```yaml
rules:
- host: todo.kiamol.local
  http:
    paths:
    - pathType: Exact          # 완전 일치
      path: /new
      backend:
        serviceName: todo-web
        portNumber: 80
    - pathType: Prefix         # 전방 일치
      path: /static
      backend:
        serviceName: todo-web
        portNumber: 80
```

`ingress-exact.yaml`로 완전 일치 규칙만 남기면 `/metrics`·`/config` 같은 경로를 인그레스 단에서 차단한다.

### 캐싱·스티키 세션

무거운 응답은 애너테이션으로 캐싱한다.

```yaml
metadata:
  name: pi
  annotations:
    nginx.ingress.kubernetes.io/proxy-buffering: "on"
    nginx.ingress.kubernetes.io/server-snippet: |
      proxy_cache static-cache;
      proxy_cache_valid 10m;
```

```bash
kubectl apply -f pi/update/ingress-with-cache.yaml            # 캐싱 적용
# pi.kiamol.local?dp=30000 — 처음엔 몇 초, 새로고침은 즉시
```

세션이 특정 파드에 묶인 앱은 레플리카가 늘면 매 요청이 다른 파드로 가서 깨진다. 스티키 세션으로 고정한다.

```bash
kubectl scale deploy/todo-web --replicas 3
kubectl logs -l app=todo-web --tail 1 --since 60s            # 400 오류 원인 확인
kubectl apply -f todo-list/update/ingress-sticky.yaml       # 스티키 세션 적용
```

!!! capture "캐시 적용 전후 비교"
    (실습 화면 캡처)

## 막혔던 점

- 파워셸에 `grep` 없음 → `. .\grep.ps1` 로드 또는 `Select-String` 대체.
- `loadBalancer.ingress` 빈 값 → 베어메탈/로컬은 외부 IP 미할당. MetalLB 설치 또는 `kubectl port-forward` 우회.
- K3s 80/443 포트 충돌 → `kubectl -n kube-system delete helmcharts.helm.cattle.io traefik` 후 Nginx 배치.
- 컨피그맵 수정 미반영 → 기존 파드는 옛 설정 유지. `kubectl rollout restart`로 재시작.
- 인그레스 API 버전 → 구버전 `networking.k8s.io/v1beta1` 제거됨. `networking.k8s.io/v1` + `service.name`/`service.port`로 마이그레이션.
