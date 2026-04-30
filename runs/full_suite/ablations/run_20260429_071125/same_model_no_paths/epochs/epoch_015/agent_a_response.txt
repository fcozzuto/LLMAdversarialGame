def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked
    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not inside(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_move = (0, 0)
        best_val = -10**9
        my = (sx, sy)
        opp = (ox, oy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            my2 = (nx, ny)
            val = 0
            for r in resources:
                myd = cheb(my2, r)
                opd = cheb(opp, r)
                cur_myd = cheb(my, r)
                cur_opd = cheb(opp, r)
                # contest-first: prefer moves that increase (opd - myd) and close our gap if we're behind
                contest = (opd - myd)
                closer = (cur_myd - myd)
                # slight penalty for moving away from the global nearest resource
                dist_to_any = min(cheb(my2, rr) for rr in resources)
                val += (5.0 * contest + 1.5 * closer - 0.15 * dist_to_any)
            # tie-break deterministically toward reducing distance to nearest resource
            if val > best_val + 1e-9:
                best_val = val
                best_move = (dx, dy)
            elif abs(val - best_val) <= 1e-9:
                if cheb((sx + dx, sy + dy), min(resources, key=lambda r: cheb(my, r))) < cheb((sx + best_move[0], sy + best_move[1]), min(resources, key=lambda r: cheb(my, r))):
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: move to improve future positioning (toward board center), avoiding obstacles
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_d = -1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = -((nx - cx) ** 2 + (ny - cy) ** 2)
        if d > best_d:
            best_d = d
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]