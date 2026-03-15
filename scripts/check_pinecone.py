import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from dotenv import load_dotenv
load_dotenv('backend/.env')
from pinecone import Pinecone
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
idx = pc.Index('kanoongpt-laws')
stats = idx.describe_index_stats()
ns = stats.get('namespaces', {})
print(f"cases : {ns.get('cases', {}).get('vector_count', 0)}")
print(f"laws  : {ns.get('laws',  {}).get('vector_count', 0)}")
print(f"total : {stats.get('total_vector_count', 0)}")
print(f"fullness: {stats.get('index_fullness', 0)}")
