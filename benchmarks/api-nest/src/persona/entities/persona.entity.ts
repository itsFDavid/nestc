export class Persona {
  id: string;
  nombre: string;
  edad: number;
  email: string;
  isActive: boolean;
  rol: string;
  telefono: string;

  constructor(id: string, nombre: string, edad: number, email: string, isActive: boolean, rol: string, telefono: string) {
    this.id = id;
    this.nombre = nombre;
    this.edad = edad;
    this.email = email;
    this.isActive = isActive;
    this.rol = rol;
    this.telefono = telefono;
  }
  
}