def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict) and "x" in r and "y" in r:
            res.append((int(r["x"]), int(r["y"])))
        elif isinstance(r, (list, tuple)) and len(r) == 2:
            res.append((int(r[0]), int(r[1])))

    def best_resource_dist(x, y):
        if not res:
            return None
        md = None
        for rx, ry in res:
            d = man(x, y, rx, ry)
            if md is None or d < md:
                md = d
        return md

    best = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dres = best_resource_dist(nx, ny)
        dop = man(nx, ny, ox, oy)
        if evader:
            score = (dres if dres is not None else 0) * 1.0 + dop * 2.0
        else:
            score = (-(dres if dres is not None else 0)) * 1.0 - dop * 2.0
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]