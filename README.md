# CinemaList

## Requisitos Previos
- Docker
- Docker Compose
- Git

## Instalación Inicial
### 1. Limpiar Docker (opcional)
Si deseas limpiar completamente tu entorno Docker, ejecuta:  
```bash
docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q) && docker rmi $(docker images -q)
```

### 2. Clonar e Iniciar el Proyecto
```bash
# Clonar el repositorio
git clone https://github.com/AnderVicario/CinemaList.git

# Entrar al directorio
cd CinemaList

# Construir e iniciar los contenedores
docker-compose build && docker-compose up -d
```

## Uso Diario
### Iniciar la Aplicación
```bash
docker-compose up -d
```

### Detener la Aplicación
```bash
docker-compose down
```

### Ver Logs (opcional)
```bash
docker-compose logs -f
```

## Notas
- La opción `-d` ejecuta los contenedores en modo "detached" (en segundo plano).  
- Para ver los logs en tiempo real, puedes usar `docker-compose logs -f`.  
- La limpieza inicial de Docker es opcional y solo debe usarse si deseas eliminar todos los contenedores e imágenes existentes. Es recomendable para que no haya conflictos con otras instalaciones.  

## Acceso
La aplicación estará disponible en:  
- (http://localhost)
