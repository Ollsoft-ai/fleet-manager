from caralgo import Algorithm, Customer, Vehicle

def test_algo():
    algorithm = Algorithm()
    vehicle = Vehicle(0.0, 0.0, "v1", "", 0)
    customers = [
        Customer(1.0, 1.0, 2.0, 2.0, "c1", True),
        Customer(2.0, 2.0, 3.0, 3.0, "c2", True),
        Customer(0.5, 0.5, 1.0, 1.0, "c3", True)
    ]
    
    result = algorithm.giveNextBestCustomers(customers, vehicle, 3.0)
    print("Test results:", result)
    assert result == ["c3", "c1", "c2"], f"Expected ['c3', 'c1', 'c2'] but got {result}"
    print("Test passed!")

if __name__ == "__main__":
    test_algo()