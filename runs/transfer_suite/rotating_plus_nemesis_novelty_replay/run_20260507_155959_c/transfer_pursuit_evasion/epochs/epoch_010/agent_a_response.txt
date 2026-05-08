def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr) or ("pursuer" in sr) or ("pursuer" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        free_neighbors = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                free_neighbors += 1

        if pursuer:
            # Chase: reduce distance; prefer central-ish positions to avoid being pinned by obstacles.
            corner_bias = min(nx, w - 1 - nx, ny, h - 1 - ny)
            score = -dist2(nx, ny, ox, oy) + 0.08 * free_neighbors + 0.04 * corner_bias
            # Slightly bias toward moving in the direction of opponent to break ties deterministically.
            score += 0.001 * ((dx * (ox - sx)) + (dy * (oy - sy)))
        else:
            # Evade: increase distance; prefer having mobility and staying away from the closest boundary.
            corner_bias = min(nx, w - 1 - nx, ny, h - 1 - ny)  # larger is more central
            score = dist2(nx, ny, ox, oy) + 0.10 * free_neighbors + 0.03 * corner_bias
            score += 0.001 * ((-dx * (ox - sx)) + (-dy * (oy - sy)))

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]