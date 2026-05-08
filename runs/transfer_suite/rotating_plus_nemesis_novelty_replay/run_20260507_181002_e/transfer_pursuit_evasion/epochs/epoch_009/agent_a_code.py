def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []):
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    targets = []
    res = observation.get("resources", None)
    if isinstance(res, dict):
        it = res.values()
    else:
        it = res if isinstance(res, list) else []
    for p in it:
        try:
            targets.append((p[0], p[1]))
        except Exception:
            pass

    if targets:
        tx, ty = min(targets, key=lambda t: (t[0] - sx) ** 2 + (t[1] - sy) ** 2)
    else:
        tx, ty = ox, oy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                if free(sx + dx, sy + dy):
                    moves.append((dx, dy))

    if not moves:
        return [0, 0]

    def score(m):
        dx, dy = m
        nx, ny = sx + dx, sy + dy
        d = (tx - nx) ** 2 + (ty - ny) ** 2
        # small bias to avoid staying still unless it's best
        stay_bias = 5 if (dx == 0 and dy == 0) else 0
        return d + stay_bias

    best = min(moves, key=lambda m: (score(m), m[0], m[1]))
    return [int(best[0]), int(best[1])]