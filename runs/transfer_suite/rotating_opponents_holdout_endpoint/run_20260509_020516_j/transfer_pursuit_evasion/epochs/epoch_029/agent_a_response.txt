def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        if it is None:
            continue
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(nx, ny):
        return abs(nx - ox) + abs(ny - oy)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if i_am_pursuer:
        # Greedy step toward opponent, avoiding obstacles; deterministic tie-breakers
        best = None
        bestd = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny)
            if best is None or d < bestd:
                best = (dx, dy)
                bestd = d
            elif d == bestd:
                # Prefer larger x-progress toward opponent then larger y-progress then non-stay
                px_best = best[0] * (1 if ox > sx else -1 if ox < sx else 0)
                px_new = dx * (1 if ox > sx else -1 if ox < sx else 0)
                py_best = best[1] * (1 if oy > sy else -1 if oy < sy else 0)
                py_new = dy * (1 if oy > sy else -1 if oy < sy else 0)
                nonstay_best = (best[0] != 0 or best[1] != 0)
                nonstay_new = (dx != 0 or dy != 0)
                if (px_new, py_new, nonstay_new) > (px_best, py_best, nonstay_best):
                    best = (dx, dy)
        if best is None:
            best = (0, 0)
        return [best[0], best[1]]

    else:
        # Evader: greedy step away; if blocked, move to maximize escape distance and keep toward center slightly
        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny)
            center_bias = -(abs(nx - cx) + abs(ny - cy))  # prefer center when distances tie
            score = (d, center_bias, (dx != 0 or dy != 0))
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        if best is None:
            best = (0, 0)
        return [best[0], best[1]]