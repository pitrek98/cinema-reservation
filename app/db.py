from cassandra.cluster import Cluster
from cassandra.policies import RoundRobinPolicy

def get_session():
    cluster = Cluster(
        contact_points=[
            "127.0.0.1"
        ],
        port=9042,
        load_balancing_policy=RoundRobinPolicy()
    )

    session = cluster.connect("cinema")
    return session