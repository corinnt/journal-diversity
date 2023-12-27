from util import info

import pandas as pd 
from tqdm import tqdm
import itertools
from concurrent.futures import ThreadPoolExecutor, wait

"""       
def multithr_iterate(all_IDs, batch_processing, batch_size=50, max_workers=15):
     Given a list of inputs to iterate through and function to handle a batch of them,
        returns a list of the results.
        :param all_IDs: list of all IDs
        :param batch_processing: function to apply to each batch

    info('Iterating through ids...')   
    zipped = False     
    if isinstance(all_IDs, zip): 
        zipped = True
        all_IDs = list(all_IDs)
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
            print("raw results: " + str(results))
            results.sort(key=lambda x: x[-1]) #thread safety
            results = [result[:-1] for result in results]
            print("results - last arg: " + str(results))
            if zipped: 
                result_lists = zip(*results)
                print("result lists: " + str(result_lists))
                final_pooled_results = [list(item) for item in result_lists]
                all_results = ([], [], ...) # TODO
            else: 
                final_pooled_results = list(itertools.chain.from_iterable(results))
                all_results = all_results + final_pooled_results

            print("pooled results: " + str(final_pooled_results))

    return all_results
"""
def multithr_iterate(all_IDs, batch_processing, batch_size=50, max_workers=15):
    """ Given a list of inputs to iterate through and function to handle a batch of them,
        returns a list of the results.
        :param all_IDs: list of all IDs (can be a list of tuples as well)
        :param batch_processing: function to apply to each batch
    """
    info('Iterating through ids...')
    all_results = []
    id_batches = [all_IDs[i:i + batch_size] for i in range(0, len(all_IDs), batch_size)]
    id_batch_pools = [id_batches[i:i + max_workers] for i in range(0, len(id_batches), max_workers)]

    for pool in tqdm(id_batch_pools):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            batch_futures = [executor.submit(batch_processing, id_batch, i) for i, id_batch in enumerate(pool)]
            wait(batch_futures)
            results = [task.result() for task in batch_futures]
            print("raw results: " + str(results))
            results.sort(key=lambda x: x[-1])  # thread safety
            results = [result[:-1] for result in results]
            print("results - last arg: " + str(results))

            if isinstance(all_IDs[0], tuple):
                # If the input is a list of tuples, unzip the results
                result_lists = zip(*results)
                pooled_results = [list(item) for item in result_lists]
            else:
                # If the input is a list, concatenate the results
                pooled_results = list(itertools.chain.from_iterable(results))

            all_results.append(pooled_results) # list of lists
            print("pooled results: " + str(pooled_results))

    if isinstance(all_IDs[0], tuple):
        # If the input is a list of tuples, create a tuple of two lists
        all_results = tuple(zip(*all_results))
        
    return all_results