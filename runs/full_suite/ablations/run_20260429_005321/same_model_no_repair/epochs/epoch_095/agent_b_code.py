def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cheb = lambda x1, y1, x2, y2: (abs(x1 - x2) if abs(x1 - x2) > abs(y1 - y2) else abs(y1 - y2))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    adj4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    def obst_pen(x, y):
        c = 0
        for ddx, ddy in adj4:
            if (x + ddx, y + ddy) in obst:
                c += 1
        return c

    # Deterministic: if already at a resource, stay.
    if (sx, sy) in obst:
        return [0, 0]
    if any((sx, sy) == (rx, ry) for rx, ry in resources):
        return [0, 0]

    best = None
    best_val = -10**18
    # Score each move by best achievable resource advantage from the next position.
    for dx, dy, nx, ny in legal:
        if resources:
            local_best = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources we can reach earlier; also value reducing our lead/closer.
                lead = do - ds
                val = 10.0 * lead - 0.7 * ds
                # Small tie-break to prefer breaking ties near center/avoid edges.
                center_bias = -0.01 * abs((w - 1) / 2 - nx) - 0.01 * abs((h - 1) / 2 - ny)
                val += center_bias
                if val > local_best:
                    local_best = val
            # Penalize getting adjacent to obstacles to reduce accidental trapping.
            move_val = local_best - 0.8 * obst_pen(nx, ny)
        else:
            # No resources visible: move to center while staying safe.
            move_val = -0.01 * abs((w - 1) / 2 - nx) - 0.01 * abs((h - 1) / 2 - ny) - 0.8 * obst_pen(nx, ny)
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then smaller distance to opponent.
        if best is None or move_val > best_val or (
            move_val == best_val and (dx, dy, cheb(nx, ny, ox, oy)) < (best[0], best[1], best[2])
        ):
            best = (dx, dy, cheb(nx, ny, ox, oy))
            best_val = move_val

    return [best[0], best[1]]