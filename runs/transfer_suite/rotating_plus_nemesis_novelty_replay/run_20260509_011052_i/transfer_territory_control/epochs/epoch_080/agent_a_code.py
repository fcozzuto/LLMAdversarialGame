def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (sx, sy))
    ox, oy = int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.add((int(p[0]), int(p[1])))
        return out

    obstacles = to_set("obstacles")
    resources = to_set("resources")

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def dman(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    nearest_res = None
    nearest_dist = 10**9
    for rx, ry in resources:
        d = dman(sx, sy, rx, ry)
        if d < nearest_dist:
            nearest_dist = d
            nearest_res = (rx, ry)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        if blocked(nx, ny):
            continue

        # Prefer moving closer to nearest resource; if no resources, move toward opponent's vicinity.
        if nearest_res is not None:
            goalx, goaly = nearest_res
            prog = dman(nx, ny, goalx, goaly)
            opp = dman(nx, ny, ox, oy)
            score = (prog, -opp)
        else:
            prog = dman(nx, ny, ox, oy)
            score = (prog, 0)

        # Tie-break deterministically: smaller (dx,dy) preferred.
        tie = (dx, dy)
        key = (score, tie)
        if best is None or key < best_score:
            best = (dx, dy)
            best_score = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]