def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_raw = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources_raw = observation.get("resources", []) or []
    resources = []
    for r in resources_raw:
        if isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
            resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_move(x, y, target):
        if (x, y) in blocked:
            return 10**9, 0
        dx = abs(x - target[0])
        dy = abs(y - target[1])
        d = dx if dx > dy else dy
        return d, 0

    best = None
    best_val = None
    for dxi, dyi in dirs:
        nx, ny = sx + dxi, sy + dyi
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        if resources:
            tbest = None
            tval = None
            for t in resources:
                d = abs(nx - t[0])
                e = abs(ny - t[1])
                dd = d if d > e else e
                if tval is None or dd < tval or (dd == tval and (t[0], t[1]) < tbest):
                    tval = dd
                    tbest = t
            # chase nearest resource; deterministic tie-break by move order
            key = (tval, nx, ny, dxi, dyi)
        else:
            # no resources: stay safe by moving away from opponent (or keep if blocked)
            d0 = max(abs(nx - ox), abs(ny - oy))
            key = (-d0, nx, ny, dxi, dyi)
        if best_val is None or key < best_val:
            best_val = key
            best = [dxi, dyi]

    if best is None:
        return [0, 0]
    return best