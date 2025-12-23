# Задание 6. Масштабирование приложений
**Выполнил студент группы P4207 Князев Илья.**

**Ссылка на репозиторий: https://github.com/EXEamp1e/task6**

## Ход работы
1. Docker registry for Linux Part 1:
![img.png](images/img.png)
![img_1.png](images/img_1.png)
2. Docker registry for Linux Parts 2 & 3:
![img_2.png](images/img_2.png)
![img_3.png](images/img_3.png)
3. Docker Orchestration Hands-on Lab:
![img_4.png](images/img_4.png)
![img_5.png](images/img_5.png)

Работа запущенного сервиса на этом узле не восстановилась, так как после перевода узла в Drain все контейнеры с него перезапускаются на других доступных узлах.
Что необходимо сделать, чтобы запустить работу службы на этом узле снова?

Чтобы задачи сервиса снова могли быть запланированы на node2, потребуется инициировать изменение в сервисе, которое заставит Swarm перераспределить реплики. Например, увеличить, а затем уменьшить количество реплик сервиса
4. Swarm stack introduction:

Количество экземпляров каждого сервиса (реплик) в развертываемом стеке настраивается декларативно в файле docker-stack.yml. 
Проверка жизнеспособности настраивается в секции deploy с помощью блока healthcheck:
```yaml
result:
  image: dockersamples/examplevotingapp_result:before
  depends_on:
    - db
  deploy:
    replicas: 2
    restart_policy:
      condition: on-failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 5s     
      timeout: 3s     
      retries: 3      
      start_period: 10s
```

5. Репозиторий со счетчиком:

Изначальные результаты нагрузочного тестирования:
![img_6.png](images/img_6.png)

Результаты после увеличения истансов до 4:
![img_7.png](images/img_7.png)

Можем увидеть увеличение RPS на 13-14%

Результаты с k8s:
![img_8.png](images/img_8.png)
Можем увидеть увеличение RPS на 6-8% в сравнении со Swarm