from caralgo import Algorithm, Customer, Vehicle

def test_algo():
    algorithm = Algorithm()
    
    # Create test vehicles
    vehicles = [
        Vehicle(0.0, 0.0, "v1", "", 0),
        Vehicle(1.0, 1.0, "v2", "", 0)
    ]
    
    # Create test customers
    customers = [
        Customer(1.0, 1.0, 2.0, 2.0, "c1", True),
        Customer(2.0, 2.0, 3.0, 3.0, "c2", True),
        Customer(0.5, 0.5, 1.0, 1.0, "c3", True)
    ]
    
    # Test assignNextCustomers with radius threshold of 3.0
    result = algorithm.assignNextCustomers(customers, vehicles, 3.0)
    print("\nTest results:")
    for vehicle_id, customer_sequence in result.items():
        print(f"Vehicle {vehicle_id}: {customer_sequence}")
    
    # Basic assertions
    assert isinstance(result, dict), "Result should be a dictionary"
    
    # Check that no customer is assigned to multiple vehicles
    all_assigned_customers = []
    for customers in result.values():
        all_assigned_customers.extend(customers)
    assert len(set(all_assigned_customers)) == len(all_assigned_customers), \
        "Each customer should only be assigned once"
    
    print("Test passed!", result)

if __name__ == "__main__":
    test_algo()