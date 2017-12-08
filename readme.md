# Read Me
To see multiple cars pick up one passenger randomly per trip, run  
```
$ python main.py RANDOM_PICKUP
```  


To see one car navigate around the environment randomly using a probabilistic road map, run  
```
$ python main.py RANDOM_NAV
```  

To see the car map its environment, run   
```
$ python main.py MAP_ONLY
```  
Eventually, the car will stop, and dots will appear on the screen. These dots represent the pixels in which the car believes there is an obstacle. Hit `M` to run K-means clustering on the dots, which will be grouped into obstacles, represented as black rectangles on the screen.  

To see the car navigate repeatedly between two randomly generated end points (once with PRM and once with RRT) with the PRM visible on the screen, run  
```
$ python main.py SHOW_PRM
```  
**Use this mode to visualize the PRM.**  

To combine `MAP_ONLY` and `RANDOM_PICKUP`, run  
```
$ python main.py MAP_AND_RANDOM_PICKUP
```  

To have multiple cars pick up multiple passengers per trip using K-means clustering to plan, run  
```
$ python main.py CLUSTERING_PICKUP
```  

To combine `MAP_ONLY` and `CLUSTERING_PICKUP`, run  
```
$ python main.py MAP_AND_CLUSTERING_PICKUP
```  

To combine `MAP_ONLY` and `SHOW_PRM`, run  
```
$ python main.py MAP_AND_SHOW_PRM
```  
**Use this mode to see the car's PRM using its mapped environment. Note that in this case and in** `SHOW_PRM`**, the car should alternate between PRM and RRT, but will use RRT if it cannot find a path using the PRM.** 

To set the number of frames for which mapping runs, change the parameter of `World.mapWorld` in `World.run` in `world.py`.   
 
To set the number of means for K-means in mapping, change the parameter `k` in the definition of `MappingAgent.generateRandomMeans` in `car.py`.  

To set the number of passengers, change the `numPassengers` variable in `World.initPassengerPickup` in `world.py`.  

To set the number of nodes in the PRM, change the `PRM.size` variable in `PRM.py`. To set the number of connections per node, change the `PRM.connsPerSample` variable in `PRM.py`.

