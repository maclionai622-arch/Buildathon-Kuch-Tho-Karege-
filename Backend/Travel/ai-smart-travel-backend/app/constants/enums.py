from enum import Enum


class SafetyLevel(str, Enum):
    safe = "Safe"
    moderate = "Moderate"
    risky = "Risky"


class CrowdLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class TrafficLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class RouteType(str, Enum):
    fastest = "fastest"
    safest = "safest"


class BudgetFit(str, Enum):
    good = "Good"
    moderate = "Moderate"
    expensive = "Expensive"


class DestinationType(str, Enum):
    tourist = "tourist"
    business = "business"
    family = "family"
    adventure = "adventure"
