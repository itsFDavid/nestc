import { IsEmail, IsNotEmpty, IsNumber, IsString, IsIn, IsPhoneNumber, IsOptional, IsBoolean } from 'class-validator';

enum Roles {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest',
}

export class CreatePersonaDto {
  @IsString()
  @IsNotEmpty()
  nombre: string;

  @IsNumber()
  @IsNotEmpty()
  edad: number;

  @IsEmail()
  @IsNotEmpty()
  email: string;
  
  @IsBoolean()
  @IsNotEmpty()
  isActive: boolean;

  @IsIn([Roles.ADMIN, Roles.USER, Roles.GUEST])
  @IsNotEmpty()
  rol: string;

  @IsString()
  @IsOptional()
  telefono: string;
}
