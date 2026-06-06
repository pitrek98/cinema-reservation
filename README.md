# Cinema reservation project

Project demonstrating handling reservations for distributed cinema system. 

## Usage
Run in venv python 3.11
To start, use

```bash
docker compose up
```
After cassandra starts
```bash
docker exec -i cassandra1 cqlsh < app/schema.cql #On Linux
Get-Content app/schema.cql | docker exec -i cassandra1 cqlsh #On Windows
```
To access CLI
```bash
python app/main.py
```
