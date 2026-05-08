def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr) or ("pursuer" in sr)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    if pursuer:
        target_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_dx, best_dy = 0, 0
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, target_corner[0], target_corner[1])
        if pursuer:
            val = -d_opp - 0.15 * d_corner
        else:
            val = d_opp + 0.10 * d_corner
        tie = (ny, nx)
        cand = (val, tie)
        if best is None or cand > best:
            best = cand
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]