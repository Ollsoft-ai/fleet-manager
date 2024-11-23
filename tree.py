import requests
import time
import redis
import json
from datetime import datetime
from anytree import Node, RenderTree, PreOrderIter
import numpy as np
import uuid
import random
from typing import List, Dict
import json

import uuid
import random
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Customer:
    coordX: float
    coordY: float
    destinationX: float
    destinationY: float
    id: str
    awaitingService: bool = False

    @classmethod
    def create_random(cls, 
                     lat_range=(48.1, 48.2), 
                     lon_range=(11.4, 11.6)) -> 'Customer':
        """Create a customer with random coordinates"""
        return cls(
            coordX=random.uniform(lat_range[0], lat_range[1]),
            coordY=random.uniform(lon_range[0], lon_range[1]),
            destinationX=random.uniform(lat_range[0], lat_range[1]),
            destinationY=random.uniform(lon_range[0], lon_range[1]),
            id=str(uuid.uuid4())
        )

    def to_dict(self) -> dict:
        """Convert customer to dictionary"""
        return {
            "awaitingService": self.awaitingService,
            "coordX": self.coordX,
            "coordY": self.coordY,
            "destinationX": self.destinationX,
            "destinationY": self.destinationY,
            "id": self.id
        }

class CustomerGenerator:
    def __init__(self, 
                 lat_range=(48.1, 48.2), 
                 lon_range=(11.4, 11.6)):
        self.lat_range = lat_range
        self.lon_range = lon_range

    def generate_customers(self, num_customers: int) -> List[Customer]:
        """Generate specified number of customers"""
        return [
            Customer.create_random(self.lat_range, self.lon_range) 
            for _ in range(num_customers)
        ]

def get_weight(custprev, custnext):
    pickup_start = np.array([custprev.destinationX, custprev.destinationY])
    cust_pickup = np.array([custnext.coordX, custnext.coordY])
    return float(np.linalg.norm(pickup_start - cust_pickup))

def make_children(root, currcust, remainingcust):
    if not remainingcust:
        return
    
    for customer in remainingcust:
        weight = get_weight(currcust, customer)
        customer_node = Node(f"{customer.id}_{weight}", parent=root)
        remaining = [c for c in remainingcust if c != customer]
        make_children(customer_node, customer, remaining)

def tree_gen(scenario_id):
    generator = CustomerGenerator()
    customers = generator.generate_customers(10)
    customer_trees = {}
    
    for customer in customers:
        root = Node(f"{customer.id}_0")
        remaining = [c for c in customers if c != customer]
        make_children(root, customer, remaining)
        customer_trees[customer.id] = root
        
        #print(f"\nCustomer {customer.id} tree:")
        #for pre, _, node in RenderTree(root):
         #   print(f"{pre}{node.name}")
    
    return customer_trees


tree_gen(scenario_id= 123455)
print("done")