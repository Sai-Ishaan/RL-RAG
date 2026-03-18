import json
import os
import uuid
from collections import Counter

class VectorStore:
    def __init__(self, storage_dir="memory/experience_db.json"):
        self.storage_dir = storage_dir
        os.makedirs(os.path.dirname(self.storage_dir), exist_ok=True)
        self.memory = self._load()

    def _load(self):
        if os.path.exists(self.storage_dir):
            with open(self.storage_dir, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _save(self):
        with open(self.storage_dir, "w") as f:
            json.dump(self.memory, f, indent=2)

    def add(self, experience):
        ###Saving verified experiences in the form Struct:
        #Structure: {id, vibe:'user request', blueprint:..., code, reward, tags:['button', 'state' etc]}
        if experience.get('reward', 0)<0.7:
            return ##saving good, high quality experiences only
        
        doc_id = str(uuid.uuid4())
        experience['id'] = doc_id
        self.memory.append(experience)
        self._save()
        print(f"[VectorStore] Memorized verified experience: {doc_id[:8]}")
        
    def search(self, query, limit=2):
        ##Retrieves top N most relevant verified experience
        query_tokens = set(query.lower().split())
        ##Using a Similar Jaccard Similarity(word overlap) as proxy

        scored_results= []
        for exp in self.memory:
            if exp['status'] != 'VERIFIED':
                continue
            #Simple similarity: 
            exp_tokens = set(exp['vibe'].lower().split())
            for comp in exp['blueprint'].get('components', []):
                exp_tokens.update(comp['name'].lower().split())

            ##Jaccard index calc
            intersection = query_tokens.intersection(exp_tokens)
            union = query_tokens.union(exp_tokens)
            score = len(intersection) / len(union) if union else 0
            scored_results.append((score, exp))

        scored_results.sort(key=lambda x: x[0], reverse=True) ##score descending order
        return [item[1] for item in scored_results[:limit] if item[0]>0.1]


