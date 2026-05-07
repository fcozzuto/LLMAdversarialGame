def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def parse_xy(v):
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return None

    resources = []
    for r in observation.get("resources") or []:
        p = parse_xy(r)
        if p is None:
            continue
        x, y = p
        if (x, y) not in obstacles and 0 <= x < w and 0 <= y < h:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None
    for (x, y) in resources:
        sd = cheb((sx, sy), (x, y))
        od = cheb((ox, oy), (x, y))
        # Prefer resources where we are closer than opponent; also break ties by shorter self distance.
        key = (sd - od * 1.15, sd, x, y)
        if best is None or key < best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try up to 4 candidate steps to avoid obstacles deterministically.
    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(cdx), int(cdy)]
    return [0, 0]