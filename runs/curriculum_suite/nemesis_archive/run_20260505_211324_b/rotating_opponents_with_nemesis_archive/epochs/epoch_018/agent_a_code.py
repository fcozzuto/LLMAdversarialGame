def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs.add((o[0], o[1]))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obs:
                    res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        # Prefer moves that maximize our ability to reach some resource before the opponent.
        # Evaluate as: (opp_dist_after - self_dist_after); higher is better.
        # Tie-breakers: shorter self_dist, then closer to center to reduce sweep-row losses.
        # Also slight penalty for moving away from the chosen "best" resource next step.
        best_adv = None
        best_sd = None
        best_r = None
        for rx, ry in res:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_sd is None or sd < best_sd)) or (adv == best_adv and sd == best_sd and (best_r is None or rx + ry < best_r[0] + best_r[1])):
                best_adv = adv
                best_sd = sd
                best_r = (rx, ry)

        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = abs(nx - cx) + abs(ny - cy)

        key = (-(best_adv if best_adv is not None else -10**9), best_sd if best_sd is not None else 10**9, center_pen)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]