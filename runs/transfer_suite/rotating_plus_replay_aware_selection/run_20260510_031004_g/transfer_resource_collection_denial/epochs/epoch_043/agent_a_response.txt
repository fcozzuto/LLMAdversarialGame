def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def best_move_toward(tx, ty):
        best = None
        best_key = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if (nx, ny) in obs:
                    continue
                d = cheb(nx, ny, tx, ty)
                # Prefer progress; tie-break deterministically by (d, nx, ny)
                key = (d, nx, ny)
                if best_key is None or key < best_key:
                    best_key = key
                    best = (dx, dy)
        return best

    if not resources:
        return [0, 0]

    # Choose resource where we are (strictly) closer than opponent; else the best "lead" (my_dist - opp_dist).
    # Deterministic tie-break by resource coordinates.
    best_r = None
    best_val = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        lead = myd - opd  # smaller is better; negative means ahead
        key = (lead, myd, rx, ry)
        if best_val is None or key < best_val:
            best_val = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    rx, ry = best_r
    mv = best_move_toward(rx, ry)
    if mv is not None:
        return [mv[0], mv[1]]

    # If all toward-moves blocked, try any safe move that reduces distance to chosen resource.
    cur_dist = cheb(sx, sy, rx, ry)
    safe = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                nd = cheb(nx, ny, rx, ry)
                safe.append((nd, nx, ny, dx, dy))
    if not safe:
        return [0, 0]
    safe.sort()
    if safe[0][0] <= cur_dist:
        return [safe[0][3], safe[0][4]]
    return [safe[0][3], safe[0][4]]