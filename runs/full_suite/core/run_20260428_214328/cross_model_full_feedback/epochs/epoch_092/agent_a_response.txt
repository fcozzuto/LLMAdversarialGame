def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_val = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # obstacle proximity penalty (deterministic, local)
        pen = 0
        for ex, ey in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1), (nx - 1, ny - 1), (nx - 1, ny + 1), (nx + 1, ny - 1), (nx + 1, ny + 1)):
            if (ex, ey) in obstacles:
                pen += 2

        # Contest-focused: prefer resources where opponent's distance advantage is smallest (or we are closer).
        if resources:
            top = -10**9
            for rx, ry in resources:
                our_d = dist_cheb((nx, ny), (rx, ry))
                opp_d = dist_cheb((ox, oy), (rx, ry))
                # Higher is better: (opp_d - our_d) favors us; slight tie-break for being closer.
                v = (opp_d - our_d) * 10 - our_d - pen
                if v > top:
                    top = v
            val = top
        else:
            # No resources: drift toward opponent to disrupt.
            val = -dist_cheb((nx, ny), (ox, oy)) - pen

        cand = (val, dx, dy)
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]