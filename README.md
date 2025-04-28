# About this project
SearchTok allows you make API calls to TikTok's search endpoint and returns a list of raw data in JSON format. 


The advantage of this tool is that it:
1. Integrates token generation and search functionality into just one single process. 

2. Circumvents rate limits and other hidden limitations by chunksizing the search timeframe into smaller intervals. 


# Getting Started
### Requirement 
Apply for TikTok's researcher credential <a href='https://developers.tiktok.com/products/research-api/'> here </a>.

### Installing
 ````bash
pip install git+https://github.com/kcinbk/SearchTok.git
````

### Importing
````python
from searchtok import search
````

### Executing a search
````python
data = search.fetch_tiktok(client_key, client_secret, search_query, start_date, end_date)
````

## Contact the author
<a href="https://kcinbk.github.io">Keenan Chen</a>.


