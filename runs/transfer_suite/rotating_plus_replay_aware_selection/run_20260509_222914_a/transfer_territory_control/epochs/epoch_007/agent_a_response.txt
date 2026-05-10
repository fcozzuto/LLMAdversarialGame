def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    my_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2 and valid(p[0], p[1]):
            my_terr.add((p[0], p[1]))

    opp_terr = []
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2 and valid(p[0], p[1]):
            opp_terr.append((p[0], p[1]))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2 and valid(p[0], p[1]):
            unclaimed.append((p[0], p[1]))

    if not unclaimed and not opp_terr:
        return [0, 0]

    def adj_my(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in my_terr:
                    c += 1
        return c

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    candidates = unclaimed if unclaimed else opp_terr
    best = None
    best_key = None
    for (x, y) in candidates:
        d1 = md(sx, sy, x, y)
        d2 = md(ox, oy, x, y)
        frontier = adj_my(x, y) if unclaimed else 0
        key = (d1 - 0.8 * frontier, -0.05 * d2, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_dist = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = md(nx, ny, tx, ty)
        key = (dist, abs(dx) + abs(dy), dx, dy)
        if best_dist is None or key < best_dist:
            best_dist = key
            best_move = [dx, dy]
    return best_move