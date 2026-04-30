def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def sqdist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy
    best_move = (0, 0)
    if resources:
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            rmin = min(sqdist((nx, ny), r) for r in resources)
            od = sqdist((nx, ny), (ox, oy))
            # minimize distance-to-resource and maximize separation
            val = (rmin * 3) - (od * 0.75)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            od = sqdist((nx, ny), (ox, oy))
            val = -od
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]