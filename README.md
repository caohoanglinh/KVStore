# Fault-tolerant Key-Value server/client using RPC (Redis clone)

Project Overview

This project implements a fault-tolerant key-value store using FastAPI Python and gRPC. It provides:

- Basic key-value operations (GET, SET, DELETE)

- Fault-tolerant communication between client and server via gRPC

The goal is to simulate a small-scale distributed system with reliable data handling.

To run a the Project result, follow the steps below:
1. Clone the Git repository

``` 
git clone https://github.com/caohoanglinh/KVStore.git
```

2. Upgrade pip (optional but recommended)

``` 
python -m pip install --upgrade pip
```

3. Install gRPC runtime and tools:

``` 
pip install grpcio grpcio-tools
```

3. Verify installation:

``` 
python -m grpc_tools.protoc --version
```

4. Navigate to the folder of the repository

``` 
cd KVStore
```

5. Install dependencies:  

``` 
pip install -r requirements.txt
```

6. Run FastAPI: 

``` 
python -m uvicorn main:app --reload
```

7. Copy the URL and add "/docs" at the end to search bar and run

8. Start the prime server:
 
``` 
python -m process.prime
```

9. Start the backup server: 

``` 
python -m backup.prime

```


