def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w, h = int(w), int(h)
    except:
        w, h = 8, 8

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    try:
        sx, sy = int(sp[0]), int(sp[1])
        ox, oy = int(op[0]), int(op[1])
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obs.add((x, y))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    best_val = None

    # Target: if opponent seems reachable, chase; otherwise go toward nearest resource if given.
    res = observation.get("resources") or []
    target = (ox, oy)
    if (not res) and "remaining_resource_count" in observation:
        pass
    elif res:
        min_md = None
        for p in res:
            if isinstance(p, (list, tuple)) and len(p) >= 2 and isinstance(p[0], int) and isinstance(p[1], int):
                x, y = p[0], p[1]
                if not inside(x, y) or (x, y) in obs:
                    continue
                md = abs(x - sx) + abs(y - sy)
                if min_md is None or md < min_md:
                    min_md = md
                    target = (x, y)

    tx, ty = target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        md = abs(nx - tx) + abs(ny - ty)
        # Slight tie-break: prefer moving when possible.
        val = (md, 0 if (dx == 0 and dy == 0) else 1)
        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best