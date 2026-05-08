def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocks

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not inb(sx, sy):
        for dx, dy in dirs:
            if inb(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    resources = observation.get("resources") or []
    res_cells = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocks:
                res_cells.append((x, y))
    unclaimed = observation.get("unclaimed_cells") or []
    un_cells = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocks:
                un_cells.append((x, y))

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_target = (ox, oy)
    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        to_opp = md((nx, ny), opp_target)

        to_res = 10**9
        if res_cells:
            for c in res_cells:
                v = md((nx, ny), c)
                if v < to_res:
                    to_res = v

        to_un = 10**9
        if un_cells:
            for c in un_cells:
                v = md((nx, ny), c)
                if v < to_un:
                    to_un = v

        # Deterministic lexicographic score:
        # primary: closer to opponent
        # secondary: prefer getting nearer to resources/unclaimed
        # tertiary: avoid staying if other moves tie
        key = (to_opp, to_res, to_un, 0 if (dx, dy) != (0, 0) else 1, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]