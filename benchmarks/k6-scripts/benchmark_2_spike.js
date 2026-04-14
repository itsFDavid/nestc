/**
 * Nest-C vs NestJS — Benchmark: Spike Test
 * Description: Simula una avalancha repentina de tráfico para evaluar el manejo de colas y bloqueos.
 * Duration: 40 seconds
 * Peak VUs: 500
 *
 * Usage:
 * Nest-C:  k6 run benchmark_2_spike.js
 * NestJS:  k6 run -e API_URL=http://127.0.0.1:3000 -e METHOD=PATCH benchmark_2_spike.js
 */

import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  scenarios: {
    spike: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "10s", target: 50 },
        { duration: "5s", target: 500 },
        { duration: "15s", target: 500 },
        { duration: "10s", target: 0 },
      ],
    },
  },
};

const BASE_URL = __ENV.API_URL || "http://127.0.0.1:8080";
const UPDATE_METHOD = __ENV.METHOD || "PUT";

export default function () {
  const params = { headers: { "Content-Type": "application/json" } };

  const createPayload = JSON.stringify({
    nombre: "K6 Tester",
    edad: 25,
    email: "k6@benchmark.com",
    isActive: true,
    rol: "admin",
    telefono: "+15551234567",
  });

  let res = http.post(`${BASE_URL}/persona`, createPayload, {
    ...params,
    tags: { name: "POST /persona" },
  });
  check(res, {
    "POST /persona status OK": (r) => r.status === 201 || r.status === 200,
  });

  let id = null;
  try {
    id = res.json("id");
  } catch (e) {}

  if (id) {
    res = http.get(`${BASE_URL}/persona`, { tags: { name: "GET /persona" } });
    check(res, { "GET /persona status 200": (r) => r.status === 200 });

    res = http.get(`${BASE_URL}/persona/${id}`, {
      tags: { name: "GET /persona/:id" },
    });
    check(res, { "GET /persona/:id status 200": (r) => r.status === 200 });

    const updatePayload = JSON.stringify({ edad: 30 });
    const updateOpts = { ...params, tags: { name: "UPDATE /persona/:id" } };

    if (UPDATE_METHOD === "PATCH") {
      res = http.patch(`${BASE_URL}/persona/${id}`, updatePayload, updateOpts);
    } else {
      res = http.put(`${BASE_URL}/persona/${id}`, updatePayload, updateOpts);
    }
    check(res, { "UPDATE /persona/:id status 200": (r) => r.status === 200 });

    res = http.del(`${BASE_URL}/persona/${id}`, null, {
      tags: { name: "DELETE /persona/:id" },
    });
    check(res, { "DELETE /persona/:id status 200": (r) => r.status === 200 });
  }

  sleep(0.01);
}
