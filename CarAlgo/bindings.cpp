#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Algorithm.h"
#include "Customer.h"
#include "Vehicle.h"

namespace py = pybind11;

PYBIND11_MODULE(caralgo, m) {
    py::class_<Customer>(m, "Customer")
        .def(py::init<float, float, float, float, std::string, bool>())
        .def_readwrite("coordX", &Customer::coordX)
        .def_readwrite("coordY", &Customer::coordY)
        .def_readwrite("destinationX", &Customer::destinationX)
        .def_readwrite("destinationY", &Customer::destinationY)
        .def_readwrite("id", &Customer::id)
        .def_readwrite("awaitingService", &Customer::awaitingService);

    py::class_<Vehicle>(m, "Vehicle")
        .def(py::init<float, float, std::string, std::string, int>())
        .def_readwrite("coordX", &Vehicle::coordX)
        .def_readwrite("coordY", &Vehicle::coordY)
        .def_readwrite("id", &Vehicle::id)
        .def_readwrite("customer_id", &Vehicle::customer_id)
        .def_readwrite("number_of_trips", &Vehicle::number_of_trips);

    py::class_<Algorithm>(m, "Algorithm")
        .def(py::init<>())
        .def("assignNextCustomers", &Algorithm::assignNextCustomers);
} 