# Architecture

# Big O

# How to run the proxy and tests

# Time spent
## Redis Backing Instance
This took a minimal amount of time, <1 hour. I have no experience with Redis so a lot of the time was spent deciding between RedisStack, and Redis.  
I learned that RedisStack includes a huge number of tools I don't need so basic Redis was all that was needed.  
I also had to decide to use Redis Cloud or not but decided not to because I didn't want to rely on some one else's server for this POC.  
After deciding on an image it was pretty easy to create the docker-compose since I have experience there and already have Docker set up on my machine.  
## Python Flask App
I spent about 2 hours creating a basic backbone here that had hardcoded info for the backing instance to just make sure I could connect and pass commands  
without problems. Once I had the connection test working, I initialized the instance with some test data and ensured that I could retrieve data without any  
caching capability. This took less than 1 hour. From there I had to decide how to provide caching with TTL and RLU capability. In searching I often found that  
Redis was recommended as a tool to do this but the 'Single Backing Instance' requirement steered me away from that. Initially I played with just using a  
normal Python Dict, but in searching around for implementing the TTL and RLU features I found the cachetools library. This provided those two features in  
a easy to use way. From there I just set a low TTL to make sure the cache was clearing, and a loop to ensure the cache capacity was being respected. This was  
about 3 hours of work.
## Makefile
This part I had the most unfamiliarity with so was expecting the most amount of time. However, this was surprisingly simple to implement. I just needed it to  
provide:
1. Launch the container
2. Set up the venv
3. Install Python packages
4. Launch the Flask app with default args
5. Test test test

## Tests

# Requirements