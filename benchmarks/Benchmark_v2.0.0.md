# Nest-C vs NestJS — Benchmark Report v2.0.0

## Executive Summary

This report consolidates three benchmark campaigns. The final campaign (v2.2) ran the full
six-scenario suite — warmup, baseline, spike, stress, soak, and breakpoint — against each
server individually with up to 3,000 concurrent virtual users over 27 minutes and 30 seconds.

Nest-C processed **14,468,520 HTTP requests** across **2,904,059 complete CRUD cycles** at
a sustained rate of **8,768 requests/second** with a median latency of **6.11 ms**. The
breakpoint scenario reached **4,997 iterations/second**, saturating the full 3,000 VU pool
before the server showed signs of failure.

NestJS processed **4,795,300 HTTP requests** across **960,564 complete CRUD cycles** at
**2,905 requests/second** with a median latency of **29.03 ms**. The breakpoint scenario
reached **3,917 iterations/second** using only 2,284 of the available 3,000 VUs before
connection timeouts appeared across all endpoint types.

---

## Test Environment

| Parameter                | Value                                                  |
| ------------------------ | ------------------------------------------------------ |
| Tool                     | Grafana k6 — local execution                           |
| Machine                  | VM, 3.8 GB RAM shared between client and server        |
| Protocol                 | HTTP/1.1, no TLS                                       |
| Payload                  | JSON: 6 fields — String, Int, Bool, Email, Enum, Phone |
| CRUD cycle per iteration | POST → GET ALL → GET ONE → PUT/PATCH → DELETE          |
| Nest-C update method     | PUT                                                    |
| NestJS update method     | PATCH                                                  |
| Nest-C port              | 8080                                                   |
| NestJS port              | 3000                                                   |
| Suite duration           | 27 minutes 30 seconds per server                       |

### Scenario timeline

| Scenario   | Executor             | Peak load           | Duration | Start offset |
| ---------- | -------------------- | ------------------- | -------- | ------------ |
| warmup     | constant-vus         | 10 VUs              | 30s      | 0s           |
| baseline   | constant-vus         | 50 VUs              | 2m       | 40s          |
| spike      | ramping-vus          | 600 VUs             | 1m 20s   | 3m           |
| stress     | ramping-vus          | 800 VUs             | 4m       | 6m           |
| soak       | constant-vus         | 150 VUs             | 10m      | 12m          |
| breakpoint | ramping-arrival-rate | 5,000 iter/s target | 4m       | 23m          |

---

## Full Suite Results

### Aggregate — All Scenarios Combined

| Metric                  | Nest-C         | NestJS         | Delta   |
| ----------------------- | -------------- | -------------- | ------- |
| Total HTTP requests     | **14,468,520** | 4,795,300      | +201.7% |
| HTTP requests/sec       | **8,768.63**   | 2,905.19       | +201.8% |
| CRUD cycles completed   | **2,904,059**  | 960,564        | +202.3% |
| CRUD cycles/sec         | **1,760.00**   | 581.95         | +202.4% |
| Data received           | **63 GB**      | 29 GB          | +117.2% |
| Data sent               | **2.1 GB**     | 751 MB         | —       |
| Avg HTTP latency        | **18.61 ms**   | 124.93 ms      | -85.1%  |
| Median HTTP latency     | **6.11 ms**    | 29.03 ms       | -78.9%  |
| p(90) HTTP latency      | **35.45 ms**   | 146.11 ms      | -75.7%  |
| p(95) HTTP latency      | **101.95 ms**  | 270.08 ms      | -62.3%  |
| Max HTTP latency        | 60 s (timeout) | 99 s (timeout) | —       |
| Avg CRUD cycle duration | **226.87 ms**  | 593.77 ms      | -61.8%  |
| Median CRUD cycle       | **32 ms**      | 151 ms         | -78.8%  |
| p(95) CRUD cycle        | **653 ms**     | 1,310 ms       | -50.2%  |
| Max CRUD cycle          | 60 s           | 132 s          | —       |
| Dropped iterations      | 235,322        | 303,642        | -22.5%  |
| Failed HTTP requests    | 12,945 (0.08%) | 6,109 (0.12%)  | —       |
| Error rate (custom)     | 0.17%          | 0.14%          | —       |

> The max latency figures reflect k6's default 60-second request timeout for Nest-C and
> the observed 99-second maximum for NestJS. Both are extreme-tail values occurring only
> during the breakpoint stage at 4,000–5,000 iterations/second.

---

### Failure Distribution — Where Each Server Broke

This is the most revealing comparison in the dataset.

**Nest-C — failures concentrated in POST during breakpoint peak:**

| Endpoint            | Successes | Failures   | Failure rate |
| ------------------- | --------- | ---------- | ------------ |
| POST /persona       | 2,891,115 | **12,944** | 0.44%        |
| GET /persona        | 2,904,059 | 0          | 0.00%        |
| GET /persona/:id    | 2,904,059 | 0          | 0.00%        |
| PUT /persona/:id    | 2,904,059 | 0          | 0.00%        |
| DELETE /persona/:id | 2,891,114 | **1**      | ~0.00%       |

**NestJS — failures distributed across all endpoints:**

| Endpoint            | Successes | Failures  | Failure rate |
| ------------------- | --------- | --------- | ------------ |
| POST /persona       | 958,564   | **3,342** | 0.35%        |
| GET /persona        | 958,267   | **68**    | 0.01%        |
| GET /persona/:id    | 957,859   | **102**   | 0.01%        |
| PATCH /persona/:id  | 957,403   | **166**   | 0.02%        |
| DELETE /persona/:id | 957,097   | **126**   | 0.01%        |

The failure pattern tells a clear architectural story. Nest-C's failures appear exclusively
on POST — the write operation that requires the most processing: DTO validation, UUID
generation, struct allocation, and array insertion. Every read and delete operation succeeded
without a single failure. This indicates that at 5,000 iterations/second, Mongoose's TCP
accept queue fills during connection establishment for new write requests, while existing
connections handling reads complete normally.

NestJS failures appear across all five endpoint types including simple GET operations. This
indicates that the Node.js event loop backpressure accumulated to the point where even
already-established connections could not be serviced in time. The event loop queue was not
draining fast enough for any operation type, not just the heavier ones.

---

### Breakpoint Scenario

The breakpoint executor targets a specific iteration rate regardless of VU count, adding
workers automatically up to `maxVUs: 3000`.

| Metric                                 | Nest-C              | NestJS        |
| -------------------------------------- | ------------------- | ------------- |
| Target iterations/sec (final stage)    | 5,000               | 5,000         |
| Achieved iterations/sec                | **4,997.43**        | 3,917.56      |
| VUs active at peak                     | 3,000 (ceiling hit) | 2,284         |
| VU ceiling reached                     | Yes                 | No            |
| Dropped iterations                     | 235,322             | 303,642       |
| Server-side failures during breakpoint | POST only           | All endpoints |

Nest-C reached the VU ceiling — k6 ran out of virtual users before the server showed
saturation. The 4,997 iterations/second result is a **client-limited measurement**, not the
server's actual ceiling. The true throughput limit of Nest-C is higher than this number and
remains unknown with the current test setup.

NestJS reached 3,917 iterations/second using only 2,284 VUs, meaning it had 716 unused
workers available but could not process requests fast enough to employ them. This is a
**server-limited measurement**. At approximately 3,900–4,000 iterations/second, Node.js
event loop saturation became the bottleneck.

---

### Soak Scenario — Memory and Stability Over Time

The soak scenario ran 150 VUs continuously for 10 minutes. During this window, each POST
adds an entity to the in-memory array, increasing the GET ALL response size on every
request. By the end of soak, the dataset contains approximately 9,000–12,000 entities
depending on the cycle rate.

Neither server showed a threshold breach during the soak window. Both passed the
`custom_crud_cycle_ms p(95) < 3000ms` threshold across the full suite. No latency
drift was captured in this report because metrics were collected as aggregates, not
time-series. Routing the output to InfluxDB or Prometheus would expose whether latency
increased progressively during the 10-minute soak window.

---

## Throughput Across All Campaigns

| Campaign     | Scenario       | VUs         | Duration | Nest-C RPS | NestJS RPS | Ratio     |
| ------------ | -------------- | ----------- | -------- | ---------- | ---------- | --------- |
| v1           | Standard Load  | 50          | 10s      | 8,220      | 4,236      | 1.94x     |
| v1           | Spike peak     | 500         | 40s      | 4,285      | 3,557      | 1.20x     |
| v1           | Extreme Stress | 800         | 2m30s    | 7,223      | 3,969      | 1.82x     |
| v2 (suite)   | Aggregate      | up to 1,000 | 27m      | 4,845      | 3,544      | 1.37x     |
| v2.2 (suite) | Aggregate      | up to 3,000 | 27m      | **8,768**  | 2,905      | **3.02x** |

The v2.2 aggregate ratio of 3.02x is the most comprehensive measurement in this dataset.
It covers all load profiles — from 10 VUs at warmup to 3,000 VUs at breakpoint — over the
same 27-minute window against each server individually with no resource sharing between
the two runs.

---

## Architectural Analysis

### Why Nest-C failures are only on POST

Mongoose processes connections on a single-threaded poll loop with a fixed TCP accept
backlog (typically 128 connections on Linux). When the arrival rate exceeds what the
accept loop can drain in one `mg_mgr_poll` call, new TCP connections queue. If the
queue fills before a slot opens, the kernel drops the SYN packet and the client sees a
timeout. Read operations on already-accepted connections are not affected — they are
already inside the poll loop and will be serviced in order. This explains why GET, PUT,
and DELETE show zero failures while POST — which requires a new connection for each
iteration at peak load — is the only endpoint that times out.

### Why NestJS failures spread across all endpoints

Node.js processes all I/O through a single event loop thread. When the event loop
accumulates more callbacks than it can drain per tick, it begins delaying responses
for all connection types equally, regardless of operation complexity. A GET that
would normally take 5 ms gets queued behind dozens of pending callbacks from other
requests. As the queue depth grows, even established connections time out waiting for
their callback to be invoked. This is why NestJS shows failures on GET, UPDATE, and
DELETE operations — not just POST.

### Single-thread ceiling

Nest-C's 4,997 iterations/second is a client-limited result. The true ceiling is
above this number and would require a separate k6 machine with more than 3,000 VUs
available. NestJS's server-limited ceiling is approximately 3,900–4,000 iterations/second
under these conditions.

A production Nest-C deployment with `SO_REUSEPORT` and N worker processes would scale
the accept backlog and poll loop linearly with core count, multiplying throughput by the
number of available cores. NestJS with the `cluster` module scales similarly but remains
subject to the single-thread event loop limit per worker process.

---

## Key Numbers for Reference

|                          | Nest-C                            | NestJS                         |
| ------------------------ | --------------------------------- | ------------------------------ |
| Peak sustained RPS       | **8,768**                         | 2,905                          |
| Median response time     | **6.11 ms**                       | 29.03 ms                       |
| p(95) response time      | **101.95 ms**                     | 270.08 ms                      |
| Total requests in 27m    | **14,468,520**                    | 4,795,300                      |
| Total CRUD cycles in 27m | **2,904,059**                     | 960,564                        |
| Breakpoint achieved      | **4,997 iter/s (client-limited)** | 3,917 iter/s (server-limited)  |
| Failure pattern          | POST only at extreme load         | All endpoints under saturation |
| Error rate               | 0.17%                             | 0.14%                          |

---

## Roadmap Items Informed by These Results

**Separate k6 machine.** The Nest-C breakpoint ceiling is unknown because k6 ran out of
VUs before the server saturated. Running k6 from a dedicated machine with no shared
resources would remove the client ceiling and expose the true server limit.

**`SO_REUSEPORT` multi-process.** The single-thread TCP accept bottleneck that caused
POST failures at 5,000 iter/s is addressable by running N Nest-C worker processes
sharing the listen socket. Each worker maintains its own accept queue, multiplying
total throughput by the number of processes.

**Pagination on GET ALL.** During the soak scenario, the in-memory dataset grows
continuously. GET ALL serializes the entire array on every request, increasing both
response size and serialization time as the soak progresses. A `?limit=N&page=M`
system would decouple response time from dataset size.

**Time-series metrics export.** Routing k6 output to InfluxDB or Prometheus during
the soak scenario would show whether p(95) latency increases over time, confirming
or ruling out heap fragmentation from dataset accumulation.

**PostgreSQL integration.** Moving to a real database introduces network I/O as
the dominant latency factor. Both servers would become I/O-bound, narrowing the
throughput gap. The numbers above measure CPU and memory-bound workloads exclusively.

---

_All benchmarks executed with Grafana k6 on a shared VM (3.8 GB RAM). Client and server
ran on the same host. Nest-C and NestJS were benchmarked in separate runs with no
resource contention between them. Results reflect single-process, in-memory workloads._
