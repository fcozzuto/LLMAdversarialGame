def choose_move(observation):
    # Defensive defaults
    x = observation.get("x", 0)
    y = observation.get("y", 0)

    # Try to read a plan if provided
    plan = observation.get("plan", None)
    if isinstance(plan, list) and len(plan) >= 2:
        dx, dy = plan[0], plan[1]
        if dx in (-1, 0, 1) and dy in (-1, 0, 1):
            return [dx, dy]

    # Determine a generic safe move towards the center of the map or origin
    mx = observation.get("map_center_x", 0)
    my = observation.get("map_center_y", 0)

    dx = 0
    dy = 0

    if x < mx:
        dx = 1
    elif x > mx:
        dx = -1

    if y < my:
        dy = 1
    elif y > my:
        dy = -1

    # If at center, prefer a random-looking small exploration by flipping to keep polite
    if dx == 0 and dy == 0:
        dx, dy = 1, 0

    # Clip to valid range (ensured by construction)
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        dx, dy = 0, 0

    return [dx, dy]
