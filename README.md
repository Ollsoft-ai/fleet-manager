![Fleet Manager Algorithm](https://raw.githubusercontent.com/Ollsoft-ai/fleet-manager/56133274c6450cb4ee2dad19d389236411624013/Fleet%20Manager%20Algorithm.gif)

## Inspiration
Creating an optimal way to allocate taxis to customers is a hard task, the fleet operator has to take into consideration a wide variety of factors. The problem is: sometimes an allocation at this point in time, while seeming best, ends up leaving the driver far away from many other customers. Also, deciding what taxi gets higher priority over a client must be thought of as well.

We modeled the problem and found out that there are many factors that can affect how attractive a client is to pick up, in the context of **time to customer**, **future opportunities** and **usual heat zones**.

## What it does
The Fleet manager application provides the **manager** easy access to **oversee** the operations. It **automatically allocates** taxis to customers in the most **fuel/time** efficient possibility. 

Managers have access to a range of **informative KPIs** to better evaluate their fleets performance, responsiveness and efficacy. Through customizable weight functions and heat map visualizations, managers can fine-tune their operations for each specific city, analyzing customer demand patterns and optimizing taxi placement based on high-traffic request areas.

## How we built it
Fleet manager uses game theory to optimize taxi allocation, similar to how chess engines evaluate moves. The system:
- Analyzes possible taxi-customer combinations with a **2-depth propagation**
- Evaluates **opportunity costs** between different allocation choices
- Implements a **dynamic decision tree** sorted by weight values
- Continuously updates assignments based on reinforcement learning **heat zones** set by the manager

This decision model enables efficient matching while maintaining flexibility for changing conditions.

## Challenges we ran into
Our biggest challenge was integrating the **C++** code of our algorithm within the overarching **python** codebase. 

Another challenging aspect was integrating the ever-changing heatmaps into the weight function. These heatmaps are adjusted based on researched and statistically probable (learned) behavior, which influences the weight assigned to each customer. 

This integration helps make the algorithm more robust for future applications where dynamic customer spawning or appearance will be a common occurrence. It ensures that when new customers request a vehicle, there is a high likelihood that one of our taxis is already nearby, allowing for quick pickups and minimal "dead" travel distance for the taxi.

## Accomplishments that we're proud of
We are happy to be able to present a solution that we believe allows for more **efficient customer taxi allocation, saving fuel, money and time**. The solution takes advantage of the different languages' strong points, combining the easy communication and **metadata analysis of python** with the **speed of C++** and the use of a **redis database to allow for fast caching** and data access. 

The program is **very lightweight**  - we were able to compile and run it on a **Raspberry Pi Zero**, which is also something we are very proud of. 

## What we learned
By learning how to **integrate C++ into Python** we implemented our algorithm in a more efficient way, both in terms of time and resource utilization. We were also very happy to be able to model the **real life problem using efficient data structures** thereby allowing for faster runtimes and an overall more effective and efficient algorithm. 

## What's next for Fleet Manager
It would be great to be able to improve our **reinforcement learning with a genetic algorithm**, thereby providing even more dynamic and optimized taxi customer allocation. Additionally, we would like to enhance the prediction component of the algorithm by increasing its throughput (depth), potentially by using **GPU acceleration** for faster data processing and more efficient decision-making.

