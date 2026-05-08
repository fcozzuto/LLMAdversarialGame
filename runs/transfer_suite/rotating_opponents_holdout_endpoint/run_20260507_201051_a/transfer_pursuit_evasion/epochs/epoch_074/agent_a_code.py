def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    env = str(observation.get("environment_name", "")).lower()
    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()

    is_pursuer = ("pursu" in sr) or ("hunter" in sr)
    if "evasion" in env:
        if ("evad" in sr) or ("escape" in sr) or ("runner" in sr):
            is_pursuer = False
    if ("pursu" in orr) or ("hunter" in orr):
        is_pursuer = False
    if ("evad" in orr) or ("escape" in orr) or ("runner" in orr):
        is_pursuer = True

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if is_pursuer:
            score = -d
        else:
            score = d
        if obstacles:
            # slight obstacle aversion to reduce collisions and wall-hugging when not beneficial
            min_ob = 10**9
            for oxp, oyp in obstacles:
                dd = cheb(nx, ny, oxp, oyp)
                if dd < min_ob:
                    min_ob = dd
            score += (0.03 if min_ob <= 1 else 0.0) * (-1 if is_pursuer else 1)
            score += (0.01 * min_ob) * (1 if is_pursuer else -1)
        if best is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]