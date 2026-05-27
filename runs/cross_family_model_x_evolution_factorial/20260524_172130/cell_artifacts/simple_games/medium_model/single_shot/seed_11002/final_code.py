def choose_move(observation):
    # Defensive defaults
    x = observation.get("player_x", 0)
    y = observation.get("player_y", 0)

    # Try simple robust heuristic across game modes
    # Priority: stay near origin if no stronger signal
    # If resources present nearby, move toward nearest resource
    # If opponent detected, attempt evasive or pursuit small step
    # Gather simple signals
    resources = observation.get("resources", [])
    opponents = observation.get("opponents", [])
    ownership = observation.get("territory", {}).get("owned", 0)

    # Helper: find nearest resource delta
    def nearest_delta(points):
        best = None
        best_dist = 1e9
        for p in points:
            dx = p[0] - x
            dy = p[1] - y
            dist = abs(dx) + abs(dy)
            if dist < best_dist:
                best_dist = dist
                best = (dx, dy)
        return best

    # If there is a resource, head toward it
    if resources:
        delta = nearest_delta(resources)
        if delta is not None:
            dx, dy = delta
            # Normalize to -1, 0, 1
            dx = max(-1, min(1, dx))
            dy = max(-1, min(1, dy))
            if dx != 0 or dy != 0:
                return [dx, dy]

    # If opponents nearby, try a small evasive or neutral move
    if opponents:
        # compute nearest opponent
        nearest = None
        best_dist = 1e9
        for o in opponents:
            ox, oy = o[0], o[1]
            dist = abs(ox - x) + abs(oy - y)
            if dist < best_dist:
                best_dist = dist
                nearest = (ox, oy)
        if nearest is not None:
            ox, oy = nearest
            dx = x - ox
            dy = y - oy
            dx = max(-1, min(1, dx))
            dy = max(-1, min(1, dy))
            if dx != 0 or dy != 0:
                return [dx, dy]
            # if on same cell, pick random safe step
            return [0, 1]

    # Territory control: move toward boundary away from owned area if needed
    # Simple heuristic: push away from center of owned region (if any data)
    if ownership is not None:
        # steer to reduce ownership value by moving outward from origin
        dx = -1 if x > 0 else 1 if x < 0 else 0
        dy = -1 if y > 0 else 1 if y < 0 else 0
        if dx != 0 or dy != 0:
            return [dx, dy]

    # Fallback: stay within bounds by minimal step toward origin
    dx = -1 if x > 0 else 1 if x < 0 else 0
    dy = -1 if y > 0 else 1 if y < 0 else 0
    if dx != 0 or dy != 0:
        return [dx, dy]

    return [0, 0]
