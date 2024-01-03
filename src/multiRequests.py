from util import info
import requests
import time
import pandas as pd 
from tqdm import tqdm
import itertools
from concurrent.futures import ThreadPoolExecutor, wait

def api_get(url):
    """ Dispatches GET requests and retries after 429 Client Error.
        Args: 
            url: str - API request url
        Returns results
    """
    try:
        response = requests.get(url)
        if response.status_code == 429: # Handle rate limiter
            #retry_after = response.headers.get('Retry-After')
            #if retry_after:
            #    time_diff = retry_after - current_time
            #   time.sleep(int(time_diff))
            #else:
            time.sleep(0.5)  
            response = requests.get(url)
        response.raise_for_status()  # Raise an exception for other 4xx or 5xx status codes
        results = response.json()
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return None
    except ValueError as e:
        print("Error decoding JSON:", e)
        return None
    return results

def api_post(url, payload, headers):
    """ Given a POST request, returns results or handles errors
        Args: 
            url: str - API Request url
            payload: json - payload to send in the body of the Request
            headers: Dictionary of HTTP Headers to send with the Request
    """
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        results = response.json()
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return 
    except ValueError as e:
        print("Error decoding JSON:", e)
        return 
    return results 

def multithr_iterate(all_IDs, batch_processing, batch_size=50, max_workers=15, tuples=False):
    """ Given a list of inputs to iterate through and function to handle a batch of them,
        returns a list of the results.
        Args:
            all_IDs: list of all IDs (can be a list of tuples as well)
            batch_processing: function to apply to each batch
            batch_size: int (default 50) for number of IDs given to each thread
            max_workers: int (default 15) for number of threads/workers
            tuples: True if result of batch processing should be a tuple
        Returns:
            list of results - inner components will be tuples if tuples=True
    """
    all_results = []
    id_batches = [all_IDs[i:i + batch_size] for i in range(0, len(all_IDs), batch_size)]
    id_batch_pools = [id_batches[i:i + max_workers] for i in range(0, len(id_batches), max_workers)]

    for pool in tqdm(id_batch_pools):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            batch_futures = [executor.submit(batch_processing, id_batch, i) for i, id_batch in enumerate(pool)]
            wait(batch_futures)
            
            results = [task.result() for task in batch_futures]
            results.sort(key=lambda x: x[-1])  # thread safety
            results = [result[:-1] for result in results] # drop indices

            if tuples:
                for tuple in results:
                    all_results.append(tuple)
            else:
                pooled_results = list(itertools.chain.from_iterable(results))
                all_results.append(pooled_results) # list of lists
        
    return all_results