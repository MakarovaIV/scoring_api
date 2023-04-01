# scoring_api
## Description
Homework 3.1 from OTUS.

**TASK:** Create tests for a system for validating HTTP API requests of the scoring service.
## Set up
Create Redis server
```commandline
docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest
```
Run redis-cli
```commandline
docker exec -it redis-stack-server redis-cli
```

Add test data to Redis server
```commandline
RPUSH 1 "Hi-Tech"
RPUSH 2 "Sci-Fi"
RPUSH 3 "Fiction" "Documentary"
```

## Run
Run application
```commandline
python3 api.py
```
### Request example for method 'online_score'
```
curl -X POST -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав", "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}' http://127.0.0.1:8080/method/
```
### Request example for method 'clients_interests'
```
curl -X POST -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95", "arguments": {"client_ids": [1, 2], "date": "19.07.2017"}}' http://127.0.0.1:8080/method/
```

## Run tests
```commandline
python3 -m unittest -v
```