#include "@nestcore/nest_core.h" 
#include "@nestcore/frozen.h" 

int main() {
    NestApp app = NestFactory_create();

    app.enable_cors = 1;
    app.payload_limit_mb = 5;

    char* env_port = getenv("PORT");
    app.port = env_port ? atoi(env_port) : 3000;

    NC_INFO("Bootstrap", "Configuración cargada en el puerto %d", app.port);
    NestFactory_listen(&app);

    return 0;
}
