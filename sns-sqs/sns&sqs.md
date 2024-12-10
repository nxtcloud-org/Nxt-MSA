# AWS SNS & SQS 가이드

## 개요

### Amazon SNS (Simple Notification Service)

* 게시자(Publisher)가 구독자(Subscriber)에게 메시지를 전송하는 관리형 서비스
* 다대다(many-to-many) 메시징을 지원하는 pub/sub 시스템
* 메시지를 여러 구독자에게 동시에 전달 가능 (fan-out)

### Amazon SQS (Simple Queue Service)

* 마이크로서비스, 분산 시스템 간의 메시지 교환을 위한 관리형 대기열 서비스
* 메시지의 손실 없이 안정적인 전달을 보장
* 비동기 처리와 서비스 간 결합도를 낮추는 데 활용

## 현재 프로젝트에서의 활용

### 사용 시나리오

1. 쇼핑몰에서 재고 부족 발생
2. SNS 토픽으로 재고 부족 알림 발행
3. 구독 중인 SQS가 메시지 수신
4. Lambda 함수가 SQS 메시지를 처리하여 공장 시스템에 생산 요청

### 구성 요소

* SNS 토픽명: `msa-topic-00`
  * 재고 부족 알림을 발행하는 채널
* SQS 큐명: `msa-queue-00`
  * 생산 요청을 처리하기 위한 메시지 대기열

## SNS-SQS 구독 설정 방법

### AWS 콘솔에서 구독 설정하기

1. SNS 콘솔 접속
2. 생성된 토픽 선택 (`msa-topic-00`)
3. "구독 생성" 클릭
4. 프로토콜: "Amazon SQS"
5. 엔드포인트: SQS 큐 ARN 선택 (`msa-queue-00`)
6. 구독 생성 완료

### 구독 설정 시 주의사항

* SQS 큐의 액세스 정책에 SNS의 메시지 전송 권한이 필요
* 큐의 리전과 토픽의 리전이 동일해야 함
* 메시지 형식과 속성이 올바르게 설정되어야 함

## 메시지 흐름

<pre><div class="relative flex flex-col rounded-lg"><div class="text-text-300 absolute pl-3 pt-2.5 text-xs"></div><div class="pointer-events-none sticky my-0.5 ml-0.5 flex items-center justify-end px-1.5 py-1 mix-blend-luminosity top-0"><div class="from-bg-300/90 to-bg-300/70 pointer-events-auto rounded-md bg-gradient-to-b p-0.5 backdrop-blur-md"><button class="flex flex-row items-center gap-1 rounded-md p-1 py-0.5 text-xs transition-opacity delay-100 hover:bg-bg-200 opacity-60 hover:opacity-100"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 256 256" class="text-text-500 mr-px -translate-y-[0.5px]"><path d="M200,32H163.74a47.92,47.92,0,0,0-71.48,0H56A16,16,0,0,0,40,48V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V48A16,16,0,0,0,200,32Zm-72,0a32,32,0,0,1,32,32H96A32,32,0,0,1,128,32Zm72,184H56V48H82.75A47.93,47.93,0,0,0,80,64v8a8,8,0,0,0,8,8h80a8,8,0,0,0,8-8V64a47.93,47.93,0,0,0-2.75-16H200Z"></path></svg><span class="text-text-200 pr-0.5">Copy</span></button></div></div><div><div class="code-block__code !my-0 !rounded-lg !text-sm !leading-relaxed"><code><span><span>[쇼핑몰] ─publish→ [SNS Topic] ─subscribe→ [SQS Queue] ─poll→ [Lambda]</span></span></code></div></div></div></pre>

## 테스트 방법

### SNS 메시지 발행 테스트

<pre><div class="relative flex flex-col rounded-lg"><div class="text-text-300 absolute pl-3 pt-2.5 text-xs">bash</div><div class="pointer-events-none sticky my-0.5 ml-0.5 flex items-center justify-end px-1.5 py-1 mix-blend-luminosity top-0"><div class="from-bg-300/90 to-bg-300/70 pointer-events-auto rounded-md bg-gradient-to-b p-0.5 backdrop-blur-md"><button class="flex flex-row items-center gap-1 rounded-md p-1 py-0.5 text-xs transition-opacity delay-100 hover:bg-bg-200 opacity-60 hover:opacity-100"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 256 256" class="text-text-500 mr-px -translate-y-[0.5px]"><path d="M200,32H163.74a47.92,47.92,0,0,0-71.48,0H56A16,16,0,0,0,40,48V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V48A16,16,0,0,0,200,32Zm-72,0a32,32,0,0,1,32,32H96A32,32,0,0,1,128,32Zm72,184H56V48H82.75A47.93,47.93,0,0,0,80,64v8a8,8,0,0,0,8,8h80a8,8,0,0,0,8-8V64a47.93,47.93,0,0,0-2.75-16H200Z"></path></svg><span class="text-text-200 pr-0.5">Copy</span></button></div></div><div><div class="code-block__code !my-0 !rounded-lg !text-sm !leading-relaxed"><code class="language-bash"><span><span>aws sns publish </span><span class="token">\</span><span>
</span></span><span><span>  --topic-arn </span><span class="token">[</span><span>SNS_TOPIC_ARN</span><span class="token">]</span><span></span><span class="token">\</span><span>
</span></span><span><span>  --message </span><span class="token">"재고 부족 알림: 상품ID=1, 수량=10"</span></span></code></div></div></div></pre>

### SQS 메시지 수신 확인

<pre><div class="relative flex flex-col rounded-lg"><div class="text-text-300 absolute pl-3 pt-2.5 text-xs">bash</div><div class="pointer-events-none sticky my-0.5 ml-0.5 flex items-center justify-end px-1.5 py-1 mix-blend-luminosity top-0"><div class="from-bg-300/90 to-bg-300/70 pointer-events-auto rounded-md bg-gradient-to-b p-0.5 backdrop-blur-md"><button class="flex flex-row items-center gap-1 rounded-md p-1 py-0.5 text-xs transition-opacity delay-100 hover:bg-bg-200 opacity-60 hover:opacity-100"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 256 256" class="text-text-500 mr-px -translate-y-[0.5px]"><path d="M200,32H163.74a47.92,47.92,0,0,0-71.48,0H56A16,16,0,0,0,40,48V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V48A16,16,0,0,0,200,32Zm-72,0a32,32,0,0,1,32,32H96A32,32,0,0,1,128,32Zm72,184H56V48H82.75A47.93,47.93,0,0,0,80,64v8a8,8,0,0,0,8,8h80a8,8,0,0,0,8-8V64a47.93,47.93,0,0,0-2.75-16H200Z"></path></svg><span class="text-text-200 pr-0.5">Copy</span></button></div></div><div><div class="code-block__code !my-0 !rounded-lg !text-sm !leading-relaxed"><code class="language-bash"><span><span>aws sqs receive-message </span><span class="token">\</span><span>
</span></span><span><span>  --queue-url </span><span class="token">[</span><span>SQS_QUEUE_URL</span><span class="token">]</span><span></span><span class="token">\</span><span>
</span></span><span><span>  --max-number-of-messages </span><span class="token">10</span></span></code></div></div></div></pre>

## 참고 사항

* SNS 메시지는 기본적으로 3시간 동안 전달 시도
* SQS 메시지의 기본 보존 기간은 4일
* Lambda 함수가 메시지 처리에 실패할 경우, DLQ(Dead Letter Queue) 구성 고려
* 운영 환경에서는 메시지 필터링과 배치 처리 설정 검토 필요
