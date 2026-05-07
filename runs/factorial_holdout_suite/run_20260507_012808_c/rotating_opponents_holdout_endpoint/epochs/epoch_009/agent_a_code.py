def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, dict):
            x = p.get("x", p.get("posx", p.get("position", (None, None))[0]))
            y = p.get("y", p.get("posy", p.get("position", (None, None))[1]))
            if x is not None and y is not None:
                obs.add((int(x), int(y)))
        else:
            try:
                obs.add((int(p[0]), int(p[1])))
            except:
                pass

    def to_xy(r):
        if isinstance(r, dict):
            x = r.get("x", r.get("posx", r.get("position", (None, None))[0]))
            y = r.get("y", r.get("posy", r.get("position", (None, None))[1]))
            if x is not None and y is not None:
                return int(x), int(y)
        else:
            try:
                return int(r[0]), int(r[1])
            except:
                return None
        return None

    resources = observation.get("resources", []) or []
    res_xy = []
    for r in resources:
        xy = to_xy(r)
        if xy is not None:
            x, y = xy
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res_xy.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target = None
    if res_xy:
        target = min(res_xy, key=lambda p: (manh(sx, sy, p[0], p[1]), p[0], p[1]))

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if target is not None:
            score = -manh(nx, ny, target[0], target[1])
        else:
            score = manh(nx, ny, ox, oy)  # move away deterministically when no resources
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    return list(best if best is not None else (0, 0))