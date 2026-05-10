def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]
    if (sx, sy) in set(tuple(r) for r in resources):
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick best resource by "gain" = how much closer we are than opponent; tie-break by closeness.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        gain = do - ds
        key = (-(gain), ds, do, rx, ry)  # smallest key => best (max gain)
        if best is None or key < best[0]:
            best = (key, (rx, ry), ds, do)
    tx, ty = best[1]

    # Evaluate local moves with obstacle-aware heuristic and opponent pressure.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = None
    best_move = (0, 0)

    # Precompute obstacle list for distance penalty (small game, keep cheap).
    obs_list = list(obstacles)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        self_d = man(nx, ny, tx, ty)
        opp_to_target = man(ox, oy, tx, ty)

        # If we step closer to any resource, prefer it deterministically.
        next_resource_bonus = 0
        for rx, ry in resources:
            if (nx, ny) == (rx, ry):
                next_resource_bonus += 10
            else:
                # Slight preference for decreasing distance to the same chosen target.
                pass

        # Opponent pressure: prefer moves that reduce (opponent_dist - self_dist) toward chosen target.
        # Also slightly prefer staying aligned to reduce time-to-collection.
        opp_d_next = man(ox, oy, tx, ty)
        pressure = opp_d_next - self_d

        # Obstacle proximity penalty (discourage hugging obstacles).
        if obs_list:
            mind = 10**9
            for px, py in obs_list:
                d = abs(nx - px) + abs(ny - py)
                if d < mind:
                    mind = d
            obstacle_pen = (0 if mind >= 2 else (2 - mind) * 0.5)
        else:
            obstacle_pen = 0

        val = (-pressure, self_d, -next_resource_bonus, obstacle_pen, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]