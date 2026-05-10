def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    rpos = []
    for r in resources:
        if isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                rpos.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                rpos.append((int(r["x"]), int(r["y"])))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            rpos.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    if rpos:
        tx, ty = min(rpos, key=lambda p: dist2(p[0], p[1], sx, sy))
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_res = dist2(nx, ny, tx, ty)
        d_opp = dist2(nx, ny, ox, oy)
        if rpos:
            key = (d_res * 10 - d_opp, dx, dy)
        else:
            key = (d_res, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]