## Hello Milvus
Install Milvus db using docker-compose and access using python

### Milvus official page for docker deployment 
https://milvus.io/docs/configure-docker.md?tab=component


### Configure Milvus with Docker Compose

##### Download a configuration file
```bash 
wget https://raw.githubusercontent.com/milvus-io/milvus/v2.5.10/configs/milvus.yaml
```

##### Download an installation file
```bash 
wget https://github.com/milvus-io/milvus/releases/download/v2.5.10/milvus-standalone-docker-compose.yml -O docker-compose.yml
```

##### Start Milvus
```bash 
sudo docker-compose up -d
```

##### additional useful commands
View container logs
```bash 
docker logs milvus-standalone
```

Stop the container (when needed)
```bash 
docker-compose down
```

### Verify if milvus is running with python 

##### hello_milvus_dc.ipynb notebook
Sample code to access Milvus

##### hello_milvus.py 
Demonstrates the basic operations of PyMilvus, a Python SDK of Milvus.
1. connect to Milvus
2. create collection
3. insert data
4. create index
5. search, query, and hybrid search on entities
6. delete entities by PK
7. drop collection

##### Execute hello_milvus.py
Go to the code folder and run notebook or execute the command
```bash 
python hello_milvus.py
```

