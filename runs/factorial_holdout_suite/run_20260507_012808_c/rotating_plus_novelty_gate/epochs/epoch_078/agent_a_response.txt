def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def clamp_step(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    if not resources:
        deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
        best = None
        for dx, dy in deltas:
            nx, ny = clamp_step(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            d = dist(nx, ny, ox, oy)
            cand = (d, dx == 0 and dy == 0)
            if best is None or cand < best:
                best = cand
                best_move = [dx, dy]
        return best_move if best is not None else [0, 0]

    # Pick resource with best chance: prefer those we reach sooner than opponent; otherwise try to steal.
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Higher is better for us; deterministic tie-break by our distance, then position.
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = clamp_step(sx + dx, sy + dy)
        blocked = (nx, ny) in obstacles
        nds = dist(nx, ny, tx, ty)
        ndo = dist(ox, oy, tx, ty)  # constant, keeps deterministic ordering
        # Prefer non-blocked, then closer to target, then also discourage letting opponent get strictly ahead next step.
        key = (blocked, nds, -((do := ndo) - nds), dx == 0 and dy == 0, nx, ny)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]
    return best_move