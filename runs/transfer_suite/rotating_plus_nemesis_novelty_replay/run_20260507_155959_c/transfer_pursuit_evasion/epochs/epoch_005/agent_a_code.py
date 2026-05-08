def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr) or ("pursuer" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    best_dx, best_dy = 0, 0
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        val = -d if pursuer else d
        tie = (ny, nx)  # deterministic
        if best_val is None:
            best_val = (val, tie)
            best_dx, best_dy = dx, dy
        else:
            cur = (val, tie)
            if cur > best_val:
                best_val = cur
                best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]