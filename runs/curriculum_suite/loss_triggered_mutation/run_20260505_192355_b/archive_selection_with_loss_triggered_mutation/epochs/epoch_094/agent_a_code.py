def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not res:
        # Deniest fallback: approach opponent (as pathing proxy)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            s = -dist((nx, ny), (ox, oy))
            if best is None or s > best[0]:
                best = (s, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # If we can reach a resource first, prioritize; also deny resources where opponent is close.
        cur_best = None
        for r in res:
            sd = dist((nx, ny), r)
            od = dist((ox, oy), r)
            # Prefer taking before opponent (od - sd positive), but keep sd small to avoid wandering.
            # Deterministic tie: include r coords.
            score = (od - sd) * 100 - sd * 3 + (15 - max(abs(nx - r[0]), abs(ny - r[1])))
            if cur_best is None or score > cur_best[0]:
                cur_best = (score, r[0], r[1], sd, od)
        if cur_best is None:
            continue
        # Secondary tie-break: prefer moves that improve our distance to that chosen resource
        final_score = cur_best[0] * 10 - cur_best[3]
        cand = (final_score, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[1], best[2]]