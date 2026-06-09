from cassandra.cluster import EXEC_PROFILE_DEFAULT, Cluster, ExecutionProfile
from cassandra.policies import ConsistencyLevel, DowngradingConsistencyRetryPolicy, RoundRobinPolicy

def get_session():
    profile = ExecutionProfile(
        retry_policy=DowngradingConsistencyRetryPolicy(),
        request_timeout=20,
    )

    cluster = Cluster(
        contact_points=[
            "127.0.0.1"
        ],
        port=9042,
        execution_profiles={EXEC_PROFILE_DEFAULT: profile}
    )

    session = cluster.connect("cinema")
    return session