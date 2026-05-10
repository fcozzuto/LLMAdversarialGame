def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    aggressive = (int(observation.get("turn_index") or 0) % 2 == 0)
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive if we are closer or tied
        if aggressive:
            # Prefer resources we can likely beat; otherwise still head to a strong one.
            key = (lead, -sd, rx, ry)
        else:
            # More opponent-avoidant: prefer far from opponent when not clearly winnable.
            key = (lead, -(sd), -(cheb(ox, oy, rx, ry)), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    # Deterministic tie-break: try the candidate with smallest collision risk, then closest to target.
    best_c = None
    best_ck = None
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        col = 1 if (nx, ny) in blocked else 0
        dist = cheb(nx, ny, tx, ty)
        # Slightly prefer diagonal when safe to reduce time.
        diag = 1 if (cdx != 0 and cdy != 0) else 0
        ck = (-col, -diag, -dist, cdx, cdy)
        if best_ck is None or ck > best_ck:
            best_ck = ck
            best_c = (cdx, cdy)

    if best_c is None:
        return [0, 0]
    return [int(best_c[0]), int(best_c[1])]