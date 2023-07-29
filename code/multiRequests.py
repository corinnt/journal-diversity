import pandas as pd 
from tqdm import tqdm
import itertools
from concurrent.futures import ThreadPoolExecutor, wait
        
def multithr_iterate(all_IDs, batch_processing, batch_size=50, max_workers=15):
    """ Given a list of inputs to iterate through and function to handle a batch of them,
        returns a list of the results.
        :param all_IDs: list of all IDs
        :param batch_processing: function to apply to each batch
    """
    print('Iterating through ids...')        

    all_results = []
    id_batches = [all_IDs[i:i + batch_size] for i in range(0, len(all_IDs), batch_size)]
    #TOGGLE FOR TEST
    #id_batches = id_batches[:100]
    id_batch_pools = [id_batches[i:i + max_workers] for i in range(0, len(id_batches), max_workers)]

    for pool in tqdm(id_batch_pools):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            batch_futures = [executor.submit(batch_processing, id_batch, i) for i, id_batch in enumerate(pool)]
            wait(batch_futures)
            results = [task.result() for task in batch_futures]
            results.sort(key=lambda x: x[1]) #thread safety
            results = [result[0] for result in results]
            
            final_pooled_results = list(itertools.chain.from_iterable(results))
            all_results = all_results + final_pooled_results

    return all_results