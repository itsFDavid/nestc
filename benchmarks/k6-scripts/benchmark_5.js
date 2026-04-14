import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 100, // Carga constante y fuerte
  duration: "2h", // ¡Dos horas sin parar!
};

// Tomamos la URL y el método del entorno (por defecto le pegará a Nest-C)
const BASE_URL = __ENV.API_URL || "http://127.0.0.1:8080";
const UPDATE_METHOD = __ENV.METHOD || "PUT";

export default function () {
  const params = { headers: { "Content-Type": "application/json" } };

  // 1. POST: Crear Persona
  const createPayload = JSON.stringify({
    nombre: "K6 Tester",
    edad: 25,
    email: "k6@benchmark.com",
    isActive: true, // <--- ¡OJO AQUÍ! Cambiado a 1
    rol: "admin",
    telefono: "5551234567",
  });

  let res = http.post(`${BASE_URL}/persona`, createPayload, params);

  // Como descubrimos que NestJS devuelve 201 y a veces Nest-C devuelve 200, validamos ambos:
  check(res, {
    "POST /persona status OK": (r) => r.status === 201 || r.status === 200,
  });

  // Extraer el ID recién creado (Ignoramos el ciclo si falla)
  let id = null;
  try {
    id = res.json("id");
  } catch (e) {}

  if (id) {
    // 2. GET ALL: Listar todos
    res = http.get(`${BASE_URL}/persona`);
    check(res, { "GET /persona status 200": (r) => r.status === 200 });

    // 3. GET ONE: Obtener el creado
    res = http.get(`${BASE_URL}/persona/${id}`);
    check(res, { "GET /persona/:id status 200": (r) => r.status === 200 });

    // 4. UPDATE: Actualizar edad
    const updatePayload = JSON.stringify({ edad: 30 });
    if (UPDATE_METHOD === "PATCH") {
      res = http.patch(`${BASE_URL}/persona/${id}`, updatePayload, params);
    } else {
      res = http.put(`${BASE_URL}/persona/${id}`, updatePayload, params);
    }
    check(res, { "UPDATE /persona/:id status 200": (r) => r.status === 200 });

    // 5. DELETE: Borrar registro
    res = http.del(`${BASE_URL}/persona/${id}`);
    check(res, { "DELETE /persona/:id status 200": (r) => r.status === 200 });
  }

  // Pequeña pausa de 10 milisegundos para simular red real y no ahogar el socket TCP de tu máquina local
  sleep(0.01);
}
