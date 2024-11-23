CXX = g++
CXXFLAGS = -std=c++11 -Wall
LDFLAGS = -luuid

SOURCES = main.cpp Customer.cpp TreeNode.cpp CustomerGenerator.cpp TreeGenerator.cpp Algorithm.cpp
OBJECTS = $(SOURCES:.cpp=.o)
EXECUTABLE = program

all: $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(CXX) $(OBJECTS) $(LDFLAGS) -o $(EXECUTABLE)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(EXECUTABLE)