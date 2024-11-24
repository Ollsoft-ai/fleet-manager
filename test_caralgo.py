import json
from caralgo import Algorithm, Customer, Vehicle

def test_algo_with_scenario():
    # Load scenario
    with open('scenario.json', 'r') as f:
        scenario = json.load(f)

    # Create algorithm instance
    algorithm = Algorithm()

    # Convert JSON data to objects
    customers = [
        Customer(
            c['coordX'], c['coordY'],
            c['destinationX'], c['destinationY'],
            c['id'], c['awaitingService']
        ) for c in scenario['customers']
    ]

    vehicles = [
        Vehicle(
            v['coordX'], v['coordY'],
            v['id'], v.get('customerId', ''),
            v['distanceTravelled']
        ) for v in scenario['vehicles']
    ]

    # Run algorithm with reasonable radius (0.1 degrees ≈ 11km)
    result = algorithm.assignNextCustomers(customers, vehicles, 0.1)

    # Print results
    print("\nAssignments:")
    for vehicle_id, customer_sequence in result.items():
        print(f"Vehicle {vehicle_id}:")
        print(f"  Next customers: {customer_sequence}")

    # Basic assertions
    assert len(result) <= len(vehicles), "More assignments than vehicles"
    assigned_customers = []
    for customers in result.values():
        assigned_customers.extend(customers)
    assert len(set(assigned_customers)) == len(assigned_customers), "Duplicate customer assignments found"

if __name__ == "__main__":
    test_algo_with_scenario()