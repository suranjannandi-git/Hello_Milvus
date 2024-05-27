# Hello Milvus
Install Milvus db using docker-compose and access using python

### Installing Milvus using docker-compose
Download milvus-standalone-docker-compose.yml and save it as docker-compose.yml 

    https://milvus.io/docs/install_standalone-docker-compose.md
    * did minor code changes to fix volumn error for local docker install 
    
Open terminal session in the same folder as docker-compose.yml file

Execute the docker compose command, this will download MongoDb and install in local docker
```bash 
docker-compose up -d
```

Verify the container is running 
```bash 
docker ps
```

View container logs
```bash 
docker logs milvus-standalone
```

Stop the container (when needed)
```bash 
docker-compose down
```

### hello_milvus_dc.ipynb notebook
Sample code to access Milvus

### hello_milvus.py 
Demonstrates the basic operations of PyMilvus, a Python SDK of Milvus.
1. connect to Milvus
2. create collection
3. insert data
4. create index
5. search, query, and hybrid search on entities
6. delete entities by PK
7. drop collection

### Execute
Go to the code folder and run notebook or execute the command
```bash 
python hello_milvus.py
```

### More details
https://github.ibm.com/Alexander-Seymour/milvus-techzone/blob/main/README.md

