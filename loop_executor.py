import asyncio

import requests

async def fetch(urls: list):
	res = []
	loop = asyncio.get_event_loop()
	futures = [loop.run_in_executor(None, requests.get, url) for url in urls]
	for response in await asyncio.gather(*futures):res.append(response)
	return res
    
    
def main():
    responses = asyncio.run(fetch(["https://molnyaonline.ru/"] * 20))
    for resp in responses:
        print(resp.ok)
        
        
        
if __name__ == "__main__":
    main()