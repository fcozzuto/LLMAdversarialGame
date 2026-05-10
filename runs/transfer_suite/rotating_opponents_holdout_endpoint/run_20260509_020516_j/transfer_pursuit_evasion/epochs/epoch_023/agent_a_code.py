def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obs_set = set()
    for p in (observation.get("obstacles", []) or []):
        if p is None:
            continue
        if isinstance(p, dict):
            x = p.get("x", p.get(0, None))
            y = p.get("y", p.get(1, None))
        else:
            x, y = (p[0], p[1]) if len(p) >= 2 else (None, None)
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    res_list = observation.get("resources", None)
    if not res_list:
        res_list = []
    res_pos = []
    for p in res_list:
        if p is None:
            continue
        if isinstance(p, dict):
            x = p.get("x", p.get(0, None))
            y = p.get("y", p.get(1, None))
        else:
            x, y = (p[0], p[1]) if len(p) >= 2 else (None, None)
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
            res_pos.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0
        if res_pos:
            md = min(d2(nx, ny, rx, ry) for rx, ry in res_pos)
            score += 1000 - md
        # avoid moving toward opponent
        score -= d2(nx, ny, ox, oy) // 2
        # slight preference for staying mobile (more valid neighbors)
        mob = 0
        for px, py in deltas:
            tx, ty = nx + px, ny + py
            if valid(tx, ty):
                mob += 1
        score += mob * 3
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]