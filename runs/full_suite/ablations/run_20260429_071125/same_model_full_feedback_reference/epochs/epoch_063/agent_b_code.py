def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res_list = observation.get("resources") or []
    resources = []
    for p in res_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # distance to nearest resource (Chebyshev)
            mind = 10**9
            hit = 0
            for rx, ry in resources:
                ddx = nx - rx
                if ddx < 0: ddx = -ddx
                ddy = ny - ry
                if ddy < 0: ddy = -ddy
                d = ddx if ddx > ddy else ddy
                if d < mind: mind = d
                if d == 0: hit = 1
            val = 1000000 * hit - mind
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Prefer moving toward center deterministically
            mx = nx - cx
            if mx < 0: mx = -mx
            my = ny - cy
            if my < 0: my = -my
            d = mx if mx > my else my
            val = -d
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]