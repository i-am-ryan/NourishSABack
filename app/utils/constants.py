# User Types
USER_TYPES = [
    "donor",        # Organizations/individuals donating food
    "recipient",    # Organizations/individuals receiving food
    "volunteer",    # People helping with transport/coordination
    "admin"        # Platform administrators
]

# Food Categories
FOOD_CATEGORIES = [
    "fresh_produce",    # Fruits, vegetables
    "dairy",           # Milk, cheese, yogurt
    "bakery",          # Bread, pastries
    "cooked_meals",    # Prepared food
    "pantry_items",    # Canned goods, dry goods
    "frozen_items"     # Frozen food
]

# Food Status
FOOD_STATUS = [
    "available",       # Ready for claiming
    "claimed",         # Someone claimed it
    "in_transit",      # Being transported
    "delivered",       # Successfully delivered
    "expired",         # Past expiry date
    "cancelled"        # Donation cancelled
]

# Volunteer Task Types
VOLUNTEER_TASKS = [
    "pickup",          # Pick up food from donor
    "delivery",        # Deliver food to recipient
    "sorting",         # Sort food at hub
    "coordination"     # Help coordinate logistics
]

# Priority Levels
PRIORITY_LEVELS = [
    "low",            # Not urgent
    "medium",         # Standard priority
    "high",           # Important
    "urgent"          # Needs immediate attention
]

# Response Messages
SUCCESS_MESSAGES = {
    "USER_CREATED": "User account created successfully",
    "LOGIN_SUCCESS": "Login successful",
    "LOGOUT_SUCCESS": "Logout successful",
    "FOOD_DONATED": "Food donation created successfully",
    "FOOD_CLAIMED": "Food claimed successfully",
    "TASK_COMPLETED": "Volunteer task completed"
}

ERROR_MESSAGES = {
    "USER_EXISTS": "User with this email already exists",
    "INVALID_CREDENTIALS": "Invalid email or password",
    "UNAUTHORIZED": "Authentication required",
    "FORBIDDEN": "Permission denied",
    "NOT_FOUND": "Resource not found",
    "VALIDATION_ERROR": "Invalid input data"
}
