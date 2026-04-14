import { Injectable } from '@nestjs/common';
import { CreatePersonaDto } from './dto/create-persona.dto';
import { UpdatePersonaDto } from './dto/update-persona.dto';
import { Persona } from './entities/persona.entity';

@Injectable()
export class PersonaService {
  private readonly personas: Persona[] = [];

  create(createPersonaDto: CreatePersonaDto) {
    const persona = new Persona(
      this.generarteUuid(),
      createPersonaDto.nombre,
      createPersonaDto.edad,
      createPersonaDto.email,
      createPersonaDto.isActive,
      createPersonaDto.rol,
      createPersonaDto.telefono
    );
    this.personas.push(persona);
    return persona;
  }

  findAll() {
    return this.personas;
  }

  findOne(id: string) {
    return this.personas.find(persona => persona.id === id);
  }

  update(id: string, updatePersonaDto: UpdatePersonaDto) {
    const personaIndex = this.personas.findIndex(persona => persona.id === id);
    if (personaIndex === -1) {
      return undefined;
    }
    this.personas[personaIndex] = { ...this.personas[personaIndex], ...updatePersonaDto };
    return this.personas[personaIndex];
  }

  remove(id: string) {
    const personaIndex = this.personas.findIndex(persona => persona.id === id);
    if (personaIndex === -1) {
      return undefined;
    }
    return this.personas.splice(personaIndex, 1)[0];
  }

  private generarteUuid(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
}
