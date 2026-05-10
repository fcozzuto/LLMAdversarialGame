def choose_move(observation):
    w = int(observation.get("grid_width") or 0)
    h = int(observation.get("grid_height") or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res_list.append((rx, ry))
    if not res_list:
        rc = observation.get("remaining_resource_count")
        if isinstance(rc, (int, float)) and rc <= 0:
            res_list = []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1)]
    best = None
    best_score = None

    def score_for(nx, ny):
        if (nx, ny) in blocked:
            return None
        # Prefer moving toward nearest resource; if none, toward opponent.
        if res_list:
            md = None
            for rx, ry in res_list:
                d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if md is None or d < md:
                    md = d
            return -md if md is not None else -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
        else:
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            return -d

    # Deterministic tie-break: iterate moves in order and only replace on strictly better score.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_for(nx, ny)
        if sc is None:
            continue
        if best_score is None or sc > best_score:
            best_score = sc
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]