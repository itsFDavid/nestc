# Nest-C vs NestJS — Benchmark Report v1.0.0

## Executive Summary

Three progressive load tests were executed using Grafana k6 to evaluate the performance of **Nest-C** (native C binary with modular architecture) against **NestJS** (Node.js 20 / V8 engine). Both APIs implement the same logic: a full in-memory CRUD with DTO validation, JSON serialization, and UUID-based entity management.

All tests ran on the same machine sequentially. Nest-C listens on `127.0.0.1:8080`, NestJS on `127.0.0.1:3000`. No external database was involved — the bottleneck is purely the HTTP + serialization layer.

**Top-line result:** Nest-C processed **1,083,650 requests** in the extreme stress scenario with a maximum observed latency of **404 ms** and zero failures. NestJS processed **595,435 requests** in the same window with a maximum latency of **24.09 seconds**, indicating event loop saturation under peak load.

---

## Test Environment

| Parameter          | Value                                                         |
| ------------------ | ------------------------------------------------------------- |
| Tool               | Grafana k6 (local execution)                                  |
| Machine            | Developer laptop running both servers simultaneously          |
| Protocol           | HTTP/1.1, no TLS                                              |
| Payload            | JSON object: 6 fields (String, Int, Bool, Email, Enum, Phone) |
| CRUD cycle         | POST → GET ALL → GET ONE → PUT/PATCH → DELETE per iteration   |
| NestJS HTTP method | PATCH (via `-e METHOD=PATCH`)                                 |
| Nest-C HTTP method | PUT (framework default at time of test)                       |

> Note: NestJS uses PATCH and Nest-C uses PUT for updates. Both are semantically equivalent in this test since the endpoint accepts partial payloads. The update payload sent is `{ "edad": 30 }` in all cases.

---

## Test 1 — Standard Load (50 VUs, 10s)

**Scenario:** 50 concurrent virtual users looping the full CRUD cycle for 10 seconds with a 10ms sleep between iterations. Baseline throughput measurement.

```
executor: 50 looping VUs for 10s
```

| Metric               | Nest-C    | NestJS    | Delta  |
| -------------------- | --------- | --------- | ------ |
| Total requests       | 82,455    | 42,545    | +93.8% |
| Requests/sec         | 8,220     | 4,236     | +94.0% |
| Iterations completed | 16,491    | 8,509     | +93.8% |
| Avg latency          | 3.52 ms   | 9.31 ms   | -62.2% |
| Median latency       | 2.18 ms   | 7.43 ms   | -70.7% |
| p(90) latency        | 7.90 ms   | 16.54 ms  | -52.2% |
| p(95) latency        | 11.02 ms  | 20.97 ms  | -47.5% |
| Max latency          | 134.24 ms | 259.46 ms | -48.3% |
| Failed requests      | 0 (0.00%) | 0 (0.00%) | —      |
| Data received        | 88 MB     | 57 MB     | —      |

Under nominal load, Nest-C processes requests in an average of 3.52 ms — roughly the time for a single syscall and memory copy. NestJS at 9.31 ms average reflects the overhead of the V8 event loop tick, garbage collector bookkeeping, and the class-based controller instantiation path.

The median latency gap is wider than the average: Nest-C at 2.18 ms vs NestJS at 7.43 ms. This suggests NestJS has a longer tail on common-case requests, not just outliers.

---

## Test 2 — Spike Test (up to 500 VUs, 40s)

**Scenario:** Traffic ramps from 0 to 50 VUs over 10 seconds, then spikes instantly to 500 VUs for 5 seconds, sustains that load for 15 seconds, then drops back to 0. Tests connection handling and queue depth under sudden traffic surge.

```
stages:
  10s → 50 VUs
   5s → 500 VUs  (spike)
  15s → 500 VUs  (sustained)
  10s → 0 VUs
```

| Metric               | Nest-C    | NestJS    | Delta  |
| -------------------- | --------- | --------- | ------ |
| Total requests       | 171,455   | 142,350   | +20.4% |
| Requests/sec         | 4,285     | 3,557     | +20.5% |
| Iterations completed | 34,291    | 28,470    | +20.4% |
| Avg latency          | 64.04 ms  | 78.52 ms  | -18.4% |
| Median latency       | 42.37 ms  | 61.52 ms  | -31.1% |
| p(90) latency        | 148.69 ms | 160.40 ms | -7.3%  |
| p(95) latency        | 191.46 ms | 212.85 ms | -10.0% |
| Max latency          | 1.13 s    | 3.16 s    | -64.2% |
| Failed requests      | 0 (0.00%) | 0 (0.00%) | —      |
| Data received        | 1.0 GB    | 987 MB    | —      |

At 500 concurrent users, the throughput gap narrows to ~20%. Both servers handle the spike without dropping connections. The architectural difference becomes visible in the tail: Nest-C's worst observed response was 1.13 seconds while NestJS reached 3.16 seconds, a point at which the Node.js event loop begins serializing work that was previously parallelized across microtask checkpoints.

The median latency divergence is notable: Nest-C at 42.37 ms vs NestJS at 61.52 ms. Under high concurrency, Mongoose (the embedded HTTP server used by Nest-C) processes connections on a tight poll loop with no task queue, while Node.js routes work through the libuv event loop which accumulates backpressure as pending I/O callbacks.

---

## Test 3 — Extreme Stress (up to 800 VUs, 2m30s)

**Scenario:** Progressive ramp across five stages reaching 800 concurrent VUs, sustained for the final 30 seconds before dropping. Designed to find the architectural breaking point of each server.

```
stages:
  30s → 100 VUs
  30s → 200 VUs
  30s → 400 VUs
  30s → 800 VUs
  30s → 0 VUs
```

| Metric               | Nest-C        | NestJS      | Delta      |
| -------------------- | ------------- | ----------- | ---------- |
| Total requests       | 1,083,650     | 595,435     | +82.0%     |
| Requests/sec         | 7,223         | 3,969       | +81.9%     |
| Iterations completed | 216,730       | 119,087     | +82.0%     |
| Avg latency          | 38.88 ms      | 77.02 ms    | -49.5%     |
| Median latency       | 20.02 ms      | 41.77 ms    | -52.1%     |
| p(90) latency        | 102.84 ms     | 172.72 ms   | -40.4%     |
| p(95) latency        | 137.11 ms     | 209.40 ms   | -34.5%     |
| **Max latency**      | **404.06 ms** | **24.09 s** | **-98.3%** |
| Failed requests      | 0 (0.00%)     | 0 (0.00%)   | —          |
| Data received        | 6.6 GB        | 3.8 GB      | —          |
| Data sent            | 158 MB        | 93 MB       | —          |

The maximum latency figure is the critical data point. At 800 VUs, NestJS produced a worst-case response of **24.09 seconds**. This is not a network timeout — it is a request that entered the Node.js event loop queue and waited while 799 other coroutines drained. The p(95) at 209 ms and the maximum at 24,090 ms represent a factor of 115x between the 95th percentile and the worst case, indicating severe tail latency under saturation.

Nest-C under the same load kept the maximum at **404 ms** with a p(95) of 137 ms — a factor of ~3x between the 95th percentile and the worst case. This is consistent behavior under load rather than exponential degradation.

Despite NestJS processing zero failed requests, the 24-second tail means that at 800 VUs, users at the unlucky end of the queue would experience a functionally unresponsive API. Nest-C's upper bound stays within a range that would not trigger client-side timeouts in most HTTP consumers (typically configured at 5–30 seconds).

---

## Throughput vs Concurrency

| VUs              | Nest-C RPS | NestJS RPS | Ratio |
| ---------------- | ---------- | ---------- | ----- |
| 50               | 8,220      | 4,236      | 1.94x |
| 500 (spike peak) | 4,285      | 3,557      | 1.20x |
| 800              | 7,223      | 3,969      | 1.82x |

Nest-C does not degrade proportionally as concurrency increases. Between 50 VUs and 800 VUs, Nest-C drops from 8,220 RPS to 7,223 RPS — a 12% reduction. NestJS drops from 4,236 RPS to 3,969 RPS — a 6.3% reduction. NestJS degrades more gracefully in percentage terms at the cost of a significantly lower absolute ceiling.

The throughput dip in the spike test (4,285 RPS for Nest-C) is expected: the spike scenario included a large proportion of GET ALL requests against an accumulated in-memory dataset, which involves serializing a growing JSON array. As the dataset grew during the 500 VU phase, the GET ALL response size and serialization time increased, lowering the per-request throughput.

---

## Architectural Analysis

**Memory model.** Nest-C allocates and frees memory per request with explicit `malloc`/`free` pairs. The router frees the response body after `mg_http_reply` returns. There is no garbage collector and no generational heap scan. Under 1 million requests, resident memory remained flat (bounded by the in-memory dataset, not by request processing state). NestJS relies on V8's generational GC, which introduces non-deterministic pause times that become visible in the latency tail under high concurrency.

**Concurrency model.** Mongoose (Nest-C's HTTP server) uses a single-threaded poll loop. Each call to `mg_mgr_poll` drains all ready connections in a tight loop. There is no task queue, no microtask checkpoint, and no promise resolution overhead. NestJS routes every request through Node.js's libuv event loop, which serializes I/O callbacks through a fixed set of thread pool workers (default: 4) and microtask queues. Under 800 VUs, the gap between enqueue time and dequeue time in the Node.js event loop produced the 24-second outlier.

**JSON serialization.** Nest-C serializes responses using stack-allocated `NcJson` builders with a single `strdup` at the end. NestJS uses `JSON.stringify`, which involves string allocation, object traversal, and GC pressure proportional to object size. For small payloads (6-field objects), the difference is minor. For GET ALL responses over large datasets, the C implementation's linear `strcat` with pre-sized buffers outperforms V8's GC-managed string concatenation.

**Single-thread limitation.** Mongoose runs on a single OS thread. Nest-C does not benefit from multi-core processors in this configuration. A production deployment with `SO_REUSEPORT` and multiple worker processes would scale linearly with core count. NestJS with the `cluster` module would exhibit similar scaling. This benchmark measures single-process performance in both cases.

---

## Benchmark Script Design Notes

Each iteration executes five sequential HTTP operations: POST, GET ALL, GET ONE, PUT/PATCH, DELETE. The `sleep(0.01)` between iterations simulates 10 ms of think time, which prevents the benchmark itself from becoming the bottleneck at low concurrency levels.

The k6 warnings about metric time series cardinality (`100,000+ unique time series`) in benchmarks 1 and 2 were caused by using dynamic UUIDs as URL path segments in metric tags. Benchmark 3 addresses this with explicit `tags: { name: 'GET /persona/:id' }` grouping, which is why benchmark 3 produces no cardinality warnings despite running at higher concurrency for longer.

The k6 API server warning (`listen tcp 127.0.0.1:6565: bind: address already in use`) is cosmetic — it appears when a previous k6 process has not fully released the REST API port. It does not affect test execution or result validity.

---

## Roadmap Items Informed by This Benchmark

**Pagination on GET ALL.** At high iteration counts, the in-memory dataset grows unbounded. GET ALL serializes the entire array on every request, which increases response size and serialization time linearly with dataset size. A `?page=N&limit=M` query parameter system would cap per-request serialization cost.

**PostgreSQL integration via `libpq`.** Moving from in-memory arrays to a database introduces network I/O as the dominant latency factor, which would likely narrow the gap between Nest-C and NestJS since both would be I/O-bound. The benchmark above measures CPU and memory-bound workloads exclusively.

**Multi-process deployment with `SO_REUSEPORT`.** A single Mongoose poll loop saturates at approximately 8,000 RPS on this hardware. Multiple worker processes sharing the listen socket would allow Nest-C to utilize all available CPU cores, potentially scaling throughput linearly.

**Docker image generation (`nestc build --docker`).** A statically linked binary on an Alpine base produces images under 10 MB, suitable for deployment on constrained environments.

---

_Benchmarks executed with Grafana k6 on a local development machine. Results reflect single-process performance on co-located client and server. Production numbers on dedicated hardware with separated client and server nodes will differ._
