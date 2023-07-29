import requests
import pandas as pd 
from tqdm import tqdm
import argparse
import itertools
from concurrent.futures import ThreadPoolExecutor, wait
        
def iterate_ids(all_IDs):
    """ 
        :param all_IDs: list of all IDs
    """
    print('Iterating through ids...')        

    BATCH_SIZE = 50
    MAX_WORKERS = 15

    all_results = []
    id_batches = [all_IDs[i:i + BATCH_SIZE] for i in range(0, len(all_IDs), BATCH_SIZE)]
    #TOGGLE FOR TEST
    #id_batches = id_batches[:100]
    id_batch_pools = [id_batches[i:i + MAX_WORKERS] for i in range(0, len(id_batches), MAX_WORKERS)]

    for pool in tqdm(id_batch_pools):
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            batch_futures = [executor.submit(process_batch, id_batch, i) for i, id_batch in enumerate(pool)]
            wait(batch_futures)
            results = [task.result() for task in batch_futures]
            results.sort(key=lambda x: x[1]) #thread safety
            results = [result[0] for result in results]
            
            final_pooled_results = list(itertools.chain.from_iterable(results))
            all_results = all_results + final_pooled_results
    return all_results

def process_batch(id_batch, index):
    """
        :param id_batch: list of 50 ids
        :param index: int for where the batch goes in the thread pool
    """
    server = "https://"
    ext = "/lookup/id"
    payload = {"ids": id_batch.tolist()}

    response = requests.post(server + ext, headers={"Content-Type": "application/json"}, json=payload)
    if response.status_code == 200:
        data = response.json()
        biotype_dict = {}

        for gene_id, gene_data in data.items():
            biotype = gene_data["biotype"]
            biotype_dict[gene_id] = biotype
        biotypes = [biotype_dict[id] for id in id_batch]
        return (biotypes, index)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return (None, index)