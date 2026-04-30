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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_move(nx, ny):
        # base: avoid collisions with opponent
        opp_d = cheb(nx, ny, ox, oy)
        s = 0
        if opp_d <= 1:
            s -= 1000
        # reward outperforming opponent on resources
        if resources:
            best_margin = -10**9
            best_ds = 10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # opponent response not modeled; use relative advantage at current turn
                margin = do - ds
                if ds < best_ds:
                    best_ds = ds
                if margin > best_margin:
                    best_margin = margin
            # prefer moving toward closer resources and increasing advantage
            s += best_margin * 50
            s += (8 - min(8, best_ds)) * 3
            # slight center preference to reduce edge trapping when margins tie
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            s -= int(cheb(nx, ny, int(cx), int(cy)))
        # micro: steer away from obstacles when possible
        for dx, dy in dirs:
            ax, ay = nx + dx, ny + dy
            if (ax, ay) in obstacles:
                s -= 1
        return s

    # If currently adjacent to opponent, focus on escaping and then grabbing nearest resource.
    esc = cheb(sx, sy, ox, oy) <= 1

    best = (-10**18, 0, 0)
    # deterministic tie-break: lexicographic order of moves
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if esc:
            s = -cheb(nx, ny, ox, oy) * 100
            # add resource pull
            if resources:
                ds = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
                s += (8 - min(8, ds)) * 10
            else:
                s += 0
        else:
            s = score_move(nx, ny)
        if s > best[0]:
            best = (s, dx, dy)

    return [int(best[1]), int(best[2])]