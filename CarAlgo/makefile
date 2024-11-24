CXX = g++
COMMON_FLAGS = -O3 -Wall -std=c++14

# Python module specific flags
PY_FLAGS = -shared -fPIC $(shell python3 -m pybind11 --includes)
PY_EXT_SUFFIX := $(shell python3-config --extension-suffix)

# Common linker flags
LDFLAGS = -luuid

# Sources and objects
SOURCES = main.cpp Customer.cpp TreeNode.cpp CustomerGenerator.cpp TreeGenerator.cpp Algorithm.cpp Vehicle.cpp
PY_SOURCES = bindings.cpp $(SOURCES)

OBJECTS = $(SOURCES:.cpp=.o)
PY_OBJECTS = $(PY_SOURCES:.cpp=.o)

# Targets
LOCAL_TARGET = program
PY_TARGET = caralgo$(PY_EXT_SUFFIX)

# Default target is Python module
.PHONY: all clean local clean-local
all: clean $(PY_TARGET)

# Python module targets
$(PY_TARGET): $(PY_OBJECTS)
	$(CXX) $(COMMON_FLAGS) $(PY_FLAGS) $(PY_OBJECTS) $(LDFLAGS) -o $@

# Local executable targets
local: clean-local $(LOCAL_TARGET)

$(LOCAL_TARGET): $(OBJECTS)
	$(CXX) $(COMMON_FLAGS) $(OBJECTS) $(LDFLAGS) -o $@
	chmod +x $(LOCAL_TARGET)

# Object compilation rules
%.o: %.cpp
	$(CXX) $(COMMON_FLAGS) $(PY_FLAGS) -c $< -o $@

# Local object compilation
%_local.o: %.cpp
	$(CXX) $(COMMON_FLAGS) -c $< -o $@

# Clean targets
clean:
	rm -f $(PY_OBJECTS) $(PY_TARGET)

clean-local:
	rm -f $(OBJECTS) $(LOCAL_TARGET)

clean-all: clean clean-local