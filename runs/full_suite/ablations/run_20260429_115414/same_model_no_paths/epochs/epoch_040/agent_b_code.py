def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in (observation.get("obstacles") or []):
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = (0, 0)
        best_val = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            val = 0
            # choose the target that makes us relatively closer than the opponent
            # deterministic: compare best margin among targets
            best_target_val = 10**18
            for tx, ty in resources:
                myd = cheb(nx, ny, tx, ty)
                oppd = cheb(ox, oy, tx, ty)
                oppd_next = oppd - 1
                if oppd_next < 0: oppd_next = 0
                # lower is better
                tv = myd - 0.9 * oppd_next
                # slight bias: prefer nearer resources even if contested
                tv += 0.03 * myd
                if tv < best_target_val:
                    best_target_val = tv
            val = best_target_val
            if val < best_val:
                best_val = val
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No resources: move to center while also not stepping into obstacles.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = (0, 0)
    best_val = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist_center = abs(nx - cx) + abs(ny - cy)
        # also prefer keeping some separation from opponent
        dist_opp = cheb(nx, ny, ox, oy)
        val = dist_center - 0.15 * dist_opp
        if val < best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]