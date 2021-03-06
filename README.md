# Публикация комиксов в группе ВКонтакте.
Скрипт публикует рандомный комикс с сайта [xkcd.com](https://xkcd.com/) в группе [ВКонтакте](https://vk.com/) от имени группы.

## Запуск

- Скачайте код
- Настройте окружение. Для этого выполните следующие действия:
  - установите Python3.x;
  - создайте виртуальное окружение [virtualenv/venv](https://docs.python.org/3/library/venv.html) для изоляции проекта и активируйте его.
  - установите необходимые зависимости:

    ```
    pip install -r requirements.txt
    ```
  - [создайте группу ВКонтакте](https://vk.com/groups?w=groups_create)
  - [создайте standalone-приложение ВКонтакте](https://vk.com/apps?act=manage)
  - получите секретный ключ для работы с [API сайта vk.com](https://vk.com/dev/), используя процедуру
  [Implicit Flow](https://vk.com/dev/implicit_flow_user) и ID вашего приложения [ВКонтакте](https://vk.com/). Вашему приложению потребуются следующие права: photos, groups, wall и offline. Укажите их через запятую в параметре запроса scope. Сохраните ключ в переменной окружения в файле ```.env``` в директории скрипта:

    ```
    VK_TOKEN=533bacf01e1165b57531ad114461ae8736d6506a3
    ```
  - узнайте ID вашей группы [здесь](https://regvk.com/id/) и сохраните его в переменной окружения в файле ```.env``` в директории скрипта:

    ```
    VK_GROUP_ID=123456789
    ```
  - запустите скрипт командой:

    ```
    python main.py
    ```
## Цели проекта
Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
