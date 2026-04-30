def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def man(a, b, x, y):
        return abs(a - x) + abs(b - y)

    def adj_obstacle_pen(x, y):
        pen = 0
        for ddx, ddy in moves:
            if ddx == 0 and ddy == 0:
                continue
            if (x + ddx, y + ddy) in obstacles:
                pen += 2
        return pen

    def best_for_move(nx, ny):
        if resources:
            best_adv = -10**9
            best_ourd = 10**9
            best_r = None
            for rx, ry in resources:
                ourd = man(nx, ny, rx, ry)
                opd = man(ox, oy, rx, ry)
                adv = opd - ourd
                if adv > best_adv or (adv == best_adv and ourd < best_ourd):
                    best_adv, best_ourd, best_r = adv, ourd, (rx, ry)
            rx, ry = best_r
            # If opponent is extremely close to that resource, reduce the commitment.
            opp_close = 1 if man(ox, oy, rx, ry) <= 1 else 0
            center_pref = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.01
            return best_adv * 10 - best_ourd - adj_obstacle_pen(nx, ny) - opp_close * 6 + center_pref
        else:
            return -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) - adj_obstacle_pen(nx, ny)

    t = observation.get("turn_index", 0)
    best = None
    for dx, dy, nx, ny in cand:
        score = best_for_move(nx, ny)
        # Deterministic tie-break: prefer moves aligned with target alternation by turn parity
        align = (dx + dy) * (1 if (t % 2 == 0) else -1)
        key = (-score, -align, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [int(best[1]), int(best[2])]