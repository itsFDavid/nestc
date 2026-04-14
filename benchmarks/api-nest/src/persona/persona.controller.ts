import { Controller, Get, Post, Body, Patch, Param, Delete, Logger } from '@nestjs/common';
import { PersonaService } from './persona.service';
import { CreatePersonaDto } from './dto/create-persona.dto';
import { UpdatePersonaDto } from './dto/update-persona.dto';

@Controller('persona')
export class PersonaController {
  private readonly logger = new Logger(PersonaController.name);
  constructor(private readonly personaService: PersonaService) {}

  @Post()
  create(@Body() createPersonaDto: CreatePersonaDto) {
    this.logger.log(`Creating persona with data: ${JSON.stringify(createPersonaDto)}`);
    return this.personaService.create(createPersonaDto);
  }

  @Get()
  findAll() {
    this.logger.log('Finding all personas');
    return this.personaService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    this.logger.log(`Finding persona with id: ${id}`);
    return this.personaService.findOne(id);
  }

  @Patch(':id')
  update(@Param('id') id: string, @Body() updatePersonaDto: UpdatePersonaDto) {
    this.logger.log(`Updating persona with id: ${id} and data: ${JSON.stringify(updatePersonaDto)}`);
    return this.personaService.update(id, updatePersonaDto);
  }

  @Delete(':id')
  remove(@Param('id') id: string) {
    this.logger.log(`Removing persona with id: ${id}`);
    return this.personaService.remove(id);
  }
}
