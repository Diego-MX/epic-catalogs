"""configuraicón de ambiente de pruebas para la conexión de SQL"""

import os

RESOURCES_AZURE = {
    "qas":{
        "sql-catallogs-feathers":{
            "user":"dbcUsername",
            "access":"dbcPassword"
        }
    }
}

ENV = os.getenv("ENV_TYPE")
