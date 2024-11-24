CXX = g++
CXXFLAGS = -O3 -Wall -shared -std=c++14 -fPIC $(shell python3 -m pybind11 --includes)
LDFLAGS = -luuid

# Get Python extension suffix
PY_EXT_SUFFIX := $(shell python3-config --extension-suffix)

# Simplified target
TARGET = caralgo$(PY_EXT_SUFFIX)

# Only include files that actually exist
SOURCES = bindings.cpp main.cpp Customer.cpp TreeNode.cpp CustomerGenerator.cpp TreeGenerator.cpp Algorithm.cpp Vehicle.cpp
OBJECTS = $(SOURCES:.cpp=.o)

# Clean all objects before building
.PHONY: all clean
all: clean $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) $(LDFLAGS) -o $@

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)

.PHONY: clean 