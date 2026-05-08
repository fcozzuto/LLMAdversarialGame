def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs if len(p) >= 2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if (sx, sy) == (ox, oy):
        return [0, 0]

    best = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = abs(nx - ox) + abs(ny - oy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]