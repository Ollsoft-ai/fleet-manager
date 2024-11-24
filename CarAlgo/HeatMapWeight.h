#pragma once
#include <vector>

class Heatmap {
public:
    struct HeatmapPoint {
        double lat;
        double lon;
        double intensity;
        
        HeatmapPoint(double lat, double lon, double intensity) 
            : lat(lat), lon(lon), intensity(intensity) {}
    };

    static float calculateHeatmapEffect(double lat, double lon);

private:
    static const std::vector<HeatmapPoint> HEATMAP_POINTS;
};