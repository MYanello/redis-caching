# Architecture
This program is centered around the redis_proxy class. We take command line arguments to define the behavior of the proxy and the backing instance of Redis. The class supplies some basic functionality:
- Initialization sets up the cache, connects to Redis, and initializes FastAPI with its routes.
- Get_data provides cache retrieval of keys if possible, and Redis retrieval if not.  
- Cachetools provides the LRU and TTL functionality.
- FastAPI to respond to API calls
- Uvicorn webserver
- Miscellaneous other methods useful for testing the class.

For testing we implement the following tools:
- Docker supplies a Redis backing instance for testing. This is defined using Docker Compose v2 (`docker compose` and not `docker-compose`).  
    Note: if you *must* use the older version of Docker Compose, you should modify the .yaml to use version 3.7 and modify the Makefile commands to have the hyphenated command
- The program is fully defined within Docker so that no Python installation is necessary for testing or usage. The container was made with the assumption that it would be using amd64 architecture, though it could likely be easily remade for arm if needed.  
- Pytest and Pytest-mock libraries are used for writing fixtures and tests  

# Time Complexity
Get from Redis - O(1), Redis dictionary lookups are in constant time  
Get from cache - O(1), Python dictionary lookups are constant time  
Add to cache - 0(1), Python dictionary appends in constant time  
Delete from cache (ttl) - O(1), this uses del, constant time  
Delete from cache (size) - O(1), this uses pop, constant time  
[Source for Cachetools implementation](https://cachetools.readthedocs.io/en/latest/#cache-implementations)  
[Source for Python ops speed](https://www.geeksforgeeks.org/complexity-cheat-sheet-for-python-operations/#)
# How to run the proxy and tests
To run the tests using Docker, simply run `make test` or `docker compose up cache_test`  
Otherwise for actual usage, modify the command with your arguments in the Compose file then run: 
```
docker compose up -d cache
```

With optional arguments being:  
--redis_host  
--redis_port  
--password (for backing Redis)  
--ttl (time to cache items)  
--k (max cache size)  
--proxy_host  
--proxy_port  
  
If you are running on Rescale with a BYOS tile, you will need to add the Docker repos to install the latest version of Docker:
```bash
$ sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
$ sudo yum install docker-ce
```
# Time spent
## Redis Backing Instance
This took a minimal amount of time, <1 hour. I have no experience with Redis so a lot of the time was spent deciding between RedisStack, and Redis.
I learned that RedisStack includes a huge number of tools I don't need so basic Redis was all that was needed.
I also had to decide to use Redis Cloud or not but decided not to because I didn't want to rely on some one else's server for this POC.
After deciding on an image it was pretty easy to create the docker-compose since I have experience there and already have Docker set up on my machine.
## Python FastAPI App
I spent about 2 hours creating a basic backbone here that had hardcoded info for the backing instance to just make sure I could connect and pass commands
without problems. Once I had the connection test working, I initialized the instance with some test data and ensured that I could retrieve data without any
caching capability. This took less than 1 hour. From there I had to decide how to provide caching with TTL and RLU capability. In searching I often found that
Redis was recommended as a tool to do this but the 'Single Backing Instance' requirement steered me away from that. Initially I played with just using a
normal Python Dict, but in searching around for implementing the TTL and RLU features I found the cachetools library. This provided those two features in
a easy to use way. From there I just set a low TTL to make sure the cache was clearing, and a loop to ensure the cache capacity was being respected. This was
about 3 hours of work.
## Makefile
This part I had some unfamiliarity with so was expecting a significant amount of time since any time I've used Make in the past, it seemed like it did a lot of magic. However, this was surprisingly simple to implement. I just needed it to
provide:
1. Launch the container
2. Set up the venv
3. Install Python packages
4. Launch pytest
5. Provide a way to launch the flask app normally
## Tests
This was by far the most time spent on the project. I learnt Pytest and Pytest-mock for this testing. I also refactored the app.py to be a class instead of just a big function so that it was easier to test. I would say this was about 8 hours of work to successfully implement all of the tests.  
One part of testing that took a fair bit of time to implement was the end-to-end test for the API. The issue I found was that the uvicorn server was blocking. To fix this I had to learn how to run the web server as a separate process as part of a fixture.  
I also found that it was hard to prove the requirement that concurrent API requests would be handled sequentially without breaking. I wrote a test using Pytest-async to test this. After writing that I wasn't satisfied that the test was actually running asynchronously since no issues popped up from that test. To prove that I wrote a sequential client test and compared the speeds. The async test was using essentially the same loop, but was consistently about twice as fast so I was content that the test was actually submitting multiple calls at the same time.
## Dockerizing
Eventually I needed to move everything into Docker to meet the final "No changes to host system" requirement. Writing the Dockerfile was pretty straightforward with the main hangup being deciding how to implement the CMD and ENTRYPOINTS and how to handle the testing. Eventually I chose to use two different services in the compose file for the proxy. One service for running in production, and another service for running the tests. This may also have been accomplished with Make using some variables, but I chose Compose because I am very comfortable in there as opposed to Makefiles. Overall this was around a 2 hour job.
# Requirements
All of the mandatory requirements were implemented successfully. 
## Redis Serialization Protocol
This was toyed with a bit in the aioredis branch, but was scrapped in favor of spending more time writing tests and trying to implement the concurrency.
## Concurrency
This was intended to be implemented initially, hence the choice of FastAPI over Flask. Time constraints prevented me from successfully getting this out the door. You can review the attempt in the conc_fastapi branch if you'd like.