def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    best = None
    for dx, dy, nx, ny in candidates:
        my_best = -10**9
        my_dist_at_best = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            adv = oppd - myd  # higher means we're closer (more advantage)
            if adv > my_best or (adv == my_best and myd < my_dist_at_best):
                my_best = adv
                my_dist_at_best = myd
        # If no resource gives positive advantage, switch to safety: move toward farthest resource from opponent
        if my_best <= 0:
            safe = -1
            safe_my = 10**9
            for rx, ry in resources:
                oppd = cheb(ox, oy, rx, ry)
                myd = cheb(nx, ny, rx, ry)
                if oppd > safe or (oppd == safe and myd < safe_my):
                    safe = oppd
                    safe_my = myd
            my_best = safe - 0.01 * safe_my
            my_dist_at_best = safe_my

        if best is None or my_best > best[0] or (my_best == best[0] and my_dist_at_best < best[1]):
            best = (my_best, my_dist_at_best, dx, dy)

    return [best[2], best[3]]