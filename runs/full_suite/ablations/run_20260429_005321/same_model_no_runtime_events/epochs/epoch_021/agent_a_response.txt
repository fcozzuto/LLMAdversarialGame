def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = -10**18

    # Deterministic target preference: favor resources where we are not further than opponent.
    def target_score(x, y, px, py):
        md = cheb(px, py, x, y)
        od = cheb(ox, oy, x, y)
        on = 1 if (px, py) == (x, y) else 0
        # If we can tie/lead, prioritize more; otherwise strongly discourage.
        lead = 1 if md <= od else 0
        return on * 10**7 + (lead * 20000) - md * 120 - (0 if lead else 900) - (od - md) * 2

    # If no resources, head to center to avoid being trapped and to set up later.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            sc = -cheb(nx, ny, tx, ty)
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return best if best is not None else [0, 0]

    res_set = set(resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Evaluate best achievable target from this move.
        if (nx, ny) in res_set:
            sc = 10**6
        else:
            sc = -cheb(nx, ny, ox, oy) * 0.5  # slight pressure
            # Choose target that maximizes our advantage.
            best_t = -10**18
            for x, y in resources:
                tsc = target_score(x, y, nx, ny)
                if tsc > best_t:
                    best_t = tsc
            sc += best_t
        # Prefer diagonal/forward slightly to escape dithering.
        sc += -0.01 * (abs(dx) + abs(dy))
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]