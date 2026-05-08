def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not candidates:
        return [0, 0]

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()
    i_pursuer = any(k in srole for k in ("pursuer", "chaser", "catch", "pursuit")) and not any(k in srole for k in ("evader", "evad"))
    if any(k in orole for k in ("pursuer", "chaser", "catch", "pursuit")):
        i_pursuer = False

    resources = observation.get("resources", None) or observation.get("resource_positions", None) or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res_list.append((int(r[0]), int(r[1])))
    if res_list:
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            score = None
            for rx, ry in res_list:
                d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                score = d if score is None else min(score, d)
            score = -score if i_pursuer is False else score
            cand = (score, nx, ny, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[3], best[4]]

    best = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        key = (-d2, nx, ny, dx, dy) if i_pursuer else (d2, nx, ny, dx, dy)
        if best is None or key < best[0]:
            best = (key,)
    return [best[0][3], best[0][4]]