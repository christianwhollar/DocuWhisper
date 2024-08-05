```
sudo service postgresql start
```

```
sudo -i -u postgres
```


```
psql
```

```
\list
```

# database: mydb

```
CREATE DATABASE mydb;
```

```
CREATE USER myuser with PASSWORD 'mypassword';
```

```
postgres=# GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
```