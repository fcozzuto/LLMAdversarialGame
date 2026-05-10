def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    want_evade = ("evader" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    ti = int(observation.get("turn_index", 0) or 0)
    parity = ti & 1

    def manhattan(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def best_clear(x, y):
        if not obstacles:
            return 10**6
        best = 10**6
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    dx0 = 0 if ox == sx else (1 if ox > sx else -1)
    dy0 = 0 if oy == sy else (1 if oy > sy else -1)

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        dist = manhattan(nx, ny, ox, oy)
        clear = best_clear(nx, ny)

        # Tie-breaker to better catch zigzags: alternate preference between "horizontal" and "vertical" pursuit.
        chase_bias = 0
        if (parity == 0 and dx != 0) or (parity == 1 and dy != 0):
            if dx == dx0 or dy == dy0:
                chase_bias = 1

        # Penalize staying too long unless it's the only contact.
        stay_pen = 1 if (dx == 0 and dy == 0) and dist != 0 else 0

        if want_evade:
            # Evade: maximize distance, but also keep away from obstacles.
            score = dist * 1000 + clear * 3 - stay_pen * 50
            better = (best_score is None) or (score > best_score)
        else:
            # Pursue: minimize distance to allow exact capture; use clearance to avoid getting blocked.
            score = -dist * 1000 + clear * 3 + chase_bias - stay_pen * 50
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best_move = [dx, dy]

    return best_move