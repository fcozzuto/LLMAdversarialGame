def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # If there is a resource, try to move towards the closest not blocked by obstacle and not into opponent
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    if resources:
        best = None
        bestd = 10**9
        for r in resources:
            rx, ry = r
            if (rx, ry) in obstacles:
                continue
            d = dist((sx, sy), (rx, ry))
            if d < bestd or (d == bestd and (rx, ry) < (best[0], best[1] if best else (10**9,10**9))):
                bestd = d
                best = (rx, ry)
        if best is not None:
            rx, ry = best
            dx = 1 if rx > sx else -1 if rx < sx else 0
            dy = 1 if ry > sy else -1 if ry < sy else 0
            if (sx+dx, sy+dy) == (ox, oy):
                dx, dy = 0, 0
            if 0 <= sx+dx < w and 0 <= sy+dy < h and (sx+dx, sy+dy) not in obstacles:
                return [dx, dy]
            # if blocked, stay or try alternative step not into obstacle/opponent
            if (sx, sy) not in obstacles:
                return [0, 0]
            return [0, 0]
    # No resources or couldn't move toward one: move to increase distance from opponent while staying valid
    best = None
    bestd = -1
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx+dx, sy+dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) == (ox, oy):
                continue
            d = dist((nx, ny), (ox, oy))
            if d > bestd or (d == bestd and (dx, dy) < (best[0], best[1]) if best else False):
                bestd = d
                best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]
    # Fallback: stay
    return [0, 0]