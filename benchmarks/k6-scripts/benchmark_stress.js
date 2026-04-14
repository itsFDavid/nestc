david@tests:~$ cat benchmark_5.js 
/**
 * Nest-C vs NestJS — Benchmark Stress Test Extremo
 * Descripción: Combina carga progresiva, picos repentinos y una fase de soak para evaluar la resiliencia total del sistema.
 * Duración total: ~24 minutos
 * Herramienta: Grafana k6
 *
 * Uso:
 * Nest-C:  k6 run benchmark_stress.js
 * NestJS:  k6 run -e API_URL=http://127.0.0.1:3000 -e METHOD=PATCH benchmark_stress.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// --- Métricas Personalizadas ---
const errorRate        = new Rate('custom_error_rate');
const crudCycleDuration = new Trend('custom_crud_cycle_ms', true);
const totalCycles      = new Counter('custom_crud_cycles_total');

// --- Configuración ---
const BASE_URL       = __ENV.API_URL     || 'http://127.0.0.1:8080';
const UPDATE_METHOD  = __ENV.METHOD      || 'PUT';
const ENDPOINT       = __ENV.ENDPOINT    || 'persona';

export const options = {
  thresholds: {
    'custom_error_rate':      ['rate<0.001'],
    'custom_crud_cycle_ms':   ['p(95)<2000'],
    'http_req_duration':      ['p(99)<5000'],
    'http_req_failed':        ['rate<0.001'],
  },
  scenarios: {
    warmup: {
      executor:    'constant-vus',
      vus:         10,
      duration:    '30s',
      startTime:   '0s',
      tags:        { scenario: 'warmup' },
    },
    baseline: {
      executor:    'constant-vus',
      vus:         50,
      duration:    '2m',
      startTime:   '40s',
      tags:        { scenario: 'baseline' },
    },
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '15s', target: 50  },
        { duration: '5s',  target: 600 },
        { duration: '30s', target: 600 },
        { duration: '20s', target: 50  },
        { duration: '10s', target: 0   },
      ],
      startTime:   '3m',
      tags:        { scenario: 'spike' },
    },
    stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '45s', target: 200 },
        { duration: '45s', target: 400 },
        { duration: '45s', target: 600 },
        { duration: '45s', target: 800 },
        { duration: '60s', target: 0   },
      ],
      startTime:   '6m',
      tags:        { scenario: 'stress' },
    },
    soak: {
      executor:    'constant-vus',
      vus:         150,
      duration:    '10m',
      startTime:   '12m',
      tags:        { scenario: 'soak' },
    },
    breakpoint: {
      executor: 'ramping-arrival-rate',
      startRate: 100,
      timeUnit:  '1s',
      preAllocatedVUs: 1500,
      maxVUs:    3000,
      stages: [
        { duration: '1m',  target: 1000  },
        { duration: '1m',  target: 2000 },
        { duration: '1m',  target: 3000 },
        { duration: '1m',  target: 5000 },
      ],
      startTime:   '23m',
      tags:        { scenario: 'breakpoint' },
    },
  },
};

// --- Payloads ---
const CREATE_PAYLOAD = JSON.stringify({
  nombre:   'K6 Tester',
  edad:     25,
  email:    'k6@benchmark.com',
  isActive: true,
  rol:      'admin',
  telefono: '+15551234567',
});

const UPDATE_PAYLOAD = JSON.stringify({ edad: 30 });
const HEADERS = { 'Content-Type': 'application/json' };

// --- Función principal ---
export default function () {
  const cycleStart = Date.now();
  let cycleOk = true;

  group('CRUD cycle', () => {

    let createRes;
    group('POST create', () => {
      createRes = http.post(
        `${BASE_URL}/${ENDPOINT}`,
        CREATE_PAYLOAD,
        { headers: HEADERS, tags: { name: `POST /${ENDPOINT}` } }
      );

      const ok = check(createRes, {
        'POST status 2xx': (r) => r.status === 200 || r.status === 201,
        'POST has id':     (r) => {
          try { return !!r.json('id'); } catch (e) { return false; }
        },
      });
      if (!ok) cycleOk = false;
      errorRate.add(!ok);
    });

    let id = null;
    try { id = createRes.json('id'); } catch (e) {}
    if (!id) {
      errorRate.add(1);
      return;
    }

    group('GET find_all', () => {
      const res = http.get(`${BASE_URL}/${ENDPOINT}`, { tags: { name: `GET /${ENDPOINT}` } });
      const ok = check(res, { 'GET ALL status 200': (r) => r.status === 200 });
      if (!ok) cycleOk = false;
      errorRate.add(!ok);
    });

    group('GET find_one', () => {
      const res = http.get(`${BASE_URL}/${ENDPOINT}/${id}`, { tags: { name: `GET /${ENDPOINT}/:id` } });
      const ok = check(res, {
        'GET ONE status 200': (r) => r.status === 200,
        'GET ONE correct id': (r) => {
          // CORREGIDO: catch (e) en lugar de catch vacío
          try { return r.json('id') === id; } catch (e) { return false; }
        },
      });
      if (!ok) cycleOk = false;
      errorRate.add(!ok);
    });

    group('UPDATE', () => {
      let res;
      const updateOpts = { headers: HEADERS, tags: { name: `${UPDATE_METHOD} /${ENDPOINT}/:id` } };

      if (UPDATE_METHOD === 'PATCH') {
        res = http.patch(`${BASE_URL}/${ENDPOINT}/${id}`, UPDATE_PAYLOAD, updateOpts);
      } else {
        res = http.put(`${BASE_URL}/${ENDPOINT}/${id}`, UPDATE_PAYLOAD, updateOpts);
      }

      const ok = check(res, { 'UPDATE status 200': (r) => r.status === 200 });
      if (!ok) cycleOk = false;
      errorRate.add(!ok);
    });

    group('DELETE', () => {
      const res = http.del(`${BASE_URL}/${ENDPOINT}/${id}`, null, { tags: { name: `DELETE /${ENDPOINT}/:id` } });
      const ok = check(res, { 'DELETE status 200': (r) => r.status === 200 });
      if (!ok) cycleOk = false;
      errorRate.add(!ok);
    });
  });

  crudCycleDuration.add(Date.now() - cycleStart);
  totalCycles.add(1);
  sleep(0.01);
}

export function setup() {
  const res = http.get(`${BASE_URL}/${ENDPOINT}`, { timeout: '5s', tags: { name: 'health_check' } });
  if (res.status !== 200) {
    throw new Error(`El servidor en ${BASE_URL} no responde. Status: ${res.status}. Abortando benchmark.`);
  }
  console.log(`Servidor OK en ${BASE_URL} — Iniciando suite de benchmarks`);
  return { base_url: BASE_URL };
}

export function teardown(data) {
  console.log(`Suite completada contra ${data.base_url}`);
}