#include "HeatMapWeight.h"
#include <cmath>
#include <algorithm>

const std::vector<Heatmap::HeatmapPoint> Heatmap::HEATMAP_POINTS = {
    // City Center (Marienplatz) - High intensity core
    {48.137154, 11.576124, 1.0},  // Center point
    {48.136154, 11.575124, 0.95},
    {48.138154, 11.577124, 0.95},
    {48.137154, 11.577124, 0.9},
    {48.136154, 11.576124, 0.9},
    // Extended city center coverage
    {48.135154, 11.574124, 0.8},
    {48.139154, 11.578124, 0.8},
    {48.137154, 11.573124, 0.8},
    {48.138154, 11.579124, 0.8},
    {48.134154, 11.575124, 0.7},
    {48.140154, 11.577124, 0.7},
    // Wide area coverage
    {48.133154, 11.573124, 0.6},
    {48.141154, 11.579124, 0.6},
    {48.137154, 11.571124, 0.6},
    {48.138154, 11.581124, 0.6},
    {48.132154, 11.574124, 0.5},
    {48.142154, 11.578124, 0.5},
    
    // Olympiapark area - Large high-intensity zone
    {48.175626, 11.551809, 0.9},  // Center point
    {48.174626, 11.550809, 0.85},
    {48.176626, 11.552809, 0.85},
    {48.175626, 11.552809, 0.8},
    {48.174626, 11.551809, 0.8},
    // Extended Olympic area
    {48.173626, 11.549809, 0.7},
    {48.177626, 11.553809, 0.7},
    {48.175626, 11.554809, 0.7},
    {48.172626, 11.550809, 0.6},
    {48.178626, 11.552809, 0.6},
    // Wide area coverage
    {48.171626, 11.548809, 0.5},
    {48.179626, 11.554809, 0.5},
    {48.175626, 11.556809, 0.5},
    {48.170626, 11.549809, 0.4},
    {48.180626, 11.553809, 0.4},

    // English Garden area - Ring around the park
    {48.158843, 11.582024, 0.8},  // Western edge
    {48.156843, 11.581024, 0.7},
    {48.154843, 11.580024, 0.7},
    {48.152843, 11.579024, 0.6},
    {48.145580, 11.586766, 0.8},  // Southern edge
    {48.144580, 11.588766, 0.7},
    {48.143580, 11.590766, 0.7},
    {48.142580, 11.592766, 0.6},
    {48.152580, 11.602766, 0.8},  // Eastern edge
    {48.154580, 11.603766, 0.7},
    {48.156580, 11.604766, 0.7},
    {48.158580, 11.605766, 0.6},
    {48.162580, 11.591766, 0.8},  // Northern edge
    {48.161580, 11.589766, 0.7},
    {48.160580, 11.587766, 0.7},
    {48.159580, 11.585766, 0.6},

    // Hauptbahnhof area
    {48.140276, 11.558404, 0.9},
    {48.141276, 11.559404, 0.85},
    {48.139276, 11.557404, 0.85},
    {48.142276, 11.560404, 0.8},
    {48.138276, 11.556404, 0.8},
    {48.143276, 11.561404, 0.6},
    {48.137276, 11.555404, 0.6},
    {48.140276, 11.562404, 0.5},
    {48.144276, 11.559404, 0.4},
    {48.136276, 11.557404, 0.4},

    // Continue with all other points...
    // [Previous points continued...]

    // Flughafen München
    {48.353234, 11.786026, 0.95},  // Terminal 1
    {48.354234, 11.787026, 0.9},
    {48.352234, 11.785026, 0.9},
    {48.355234, 11.788026, 0.85},
    {48.351234, 11.784026, 0.85},
    {48.357234, 11.790026, 0.8},  // Terminal 2
    {48.358234, 11.791026, 0.75},
    {48.356234, 11.789026, 0.75},
    {48.359234, 11.792026, 0.7},
    {48.355234, 11.788026, 0.7}
};

float Heatmap::calculateHeatmapEffect(double lat, double lon) {
    float max_effect = 0.0f;
    
    for (const auto& point : HEATMAP_POINTS) {
        double distance = std::sqrt(
            std::pow(lat - point.lat, 2) + 
            std::pow(lon - point.lon, 2)
        );

        if (distance < 0.005) {  // About 500m radius
            float effect = static_cast<float>(point.intensity * (0.01 - distance) / 0.01);
            max_effect = std::max(max_effect, effect);
        }
    }

    return max_effect;
}