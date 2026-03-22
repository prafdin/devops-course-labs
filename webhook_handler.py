import os

import json

from flask import Flask, request


app = Flask(__name__)


APP_PATH = "/home/vanya/catty-reminders-app" 

SERVICE_NAME = "catty-app"


@app.route('/', methods=['POST'])

def webhook():

    # Проверяем, что это JSON от GitHub [cite: 88]

    data = request.get_json()

    if not data:

        return 'No JSON data', 400


    # Извлекаем ветку (например, "refs/heads/main") 

    ref = data.get('ref', '')

    if not ref:

        return 'No ref found', 400

    

    branch = ref.split('/')[-1] # Получаем чистое имя ветки: "main" или "dev"

    sha = data.get('after', 'unknown') # SHA коммита из вебхука


    print(f"Получено событие для ветки: {branch}, SHA: {sha}")


    # Последовательность команд для деплоя [cite: 96, 99]

    # 1. Переходим в папку

    # 2. Скачиваем изменения

    # 3. Жестко переключаемся на нужную ветку и сбрасываем состояние до origin

    # 4. Записываем SHA в .env (используем кавычки для безопасности)

    commands = [

        f"cd {APP_PATH}",

        "git fetch origin",

        f"git reset --hard origin/{branch}",

        f"echo 'DEPLOY_REF={sha}' > {APP_PATH}/.env",

        f"sudo systemctl restart {SERVICE_NAME}"

    ]


    full_command = " && ".join(commands)

    exit_code = os.system(full_command)


    if exit_code == 0:

        print(f"Успешно развернута ветка {branch} (SHA: {sha})")

        return f"OK: Deployed branch {branch}", 200

    else:

        print(f"Ошибка при выполнении команд. Код: {exit_code}")

        return 'Error: Deployment failed', 500


if __name__ == '__main__':

    # Слушаем порт 8080, как указано в задании 

    app.run(host='0.0.0.0', port=8080)
