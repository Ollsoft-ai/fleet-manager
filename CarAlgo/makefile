CXX = g++
CXXFLAGS = -O3 -Wall -shared -std=c++11 -fPIC $(shell python3 -m pybind11 --includes)
LDFLAGS = -luuid

# Get Python extension suffix (e.g., .cpython-39-x86_64-linux-gnu.so)
PY_EXT_SUFFIX := $(shell python3-config --extension-suffix)

# The output shared library name
TARGET = caralgo$(PY_EXT_SUFFIX)

# Add Vehicle.cpp to the sources
SOURCES = Algorithm.cpp Customer.cpp TreeNode.cpp CustomerGenerator.cpp TreeGenerator.cpp Vehicle.cpp bindings.cpp
OBJECTS = $(SOURCES:.cpp=.o)

all: clean $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) $(LDFLAGS) -o $(TARGET)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)