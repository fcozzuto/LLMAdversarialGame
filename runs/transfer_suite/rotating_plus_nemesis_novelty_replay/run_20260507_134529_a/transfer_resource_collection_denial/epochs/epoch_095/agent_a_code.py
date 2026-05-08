def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((o[0], o[1]))
        elif isinstance(o, dict):
            p = o.get("position") or o.get("pos")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                blocked.add((p[0], p[1]))
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked
    resources = observation.get("resources") or []
    res_pos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_pos.append((r[0], r[1]))
        elif isinstance(r, dict):
            p = r.get("position") or r.get("pos")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                res_pos.append((p[0], p[1]))
    def cheb(x1, y1, x2, y2):
        a, b = x1 - x2, y1 - y2
        if a < 0: a = -a
        if b < 0: b = -b
        return a if a > b else b
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_score = -10**18
    if res_pos:
        target = min(res_pos, key=lambda p: cheb(sx, sy, p[0], p[1]))
        tx, ty = target
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            score = 1000 - cheb(nx, ny, tx, ty) * 10 + cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best = [dx, dy]
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            score = cheb(nx, ny, ox, oy) * 10 - cheb(nx, ny, sx, sy)
            if score > best_score:
                best_score = score
                best = [dx, dy]
    return best