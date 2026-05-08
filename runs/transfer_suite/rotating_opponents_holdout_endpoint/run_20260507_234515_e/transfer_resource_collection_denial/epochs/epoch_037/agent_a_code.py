def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    resources = observation.get("resources") or []
    ox, oy = observation["opponent_position"]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_score = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        move_score = -10**18
        for rx, ry in resources:
            myd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            center_pen = abs(nx - cx) + abs(ny - cy)
            if (nx, ny) == (rx, ry):
                s = 10**7 + (oppd - myd) * 1000 - myd - center_pen * 2
            else:
                # Prefer resources where we are closer than opponent; also prefer faster pickup and central positioning.
                s = (oppd - myd) * 1200 - myd * 3 - center_pen * 2
            if s > move_score:
                move_score = s
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)
        elif move_score == best_score:
            # deterministic tie-break: smaller my distance to closest resource
            def min_myd_at(cellx, celly):
                mm = 10**9
                for rx, ry in resources:
                    mm = min(mm, abs(cellx - rx) + abs(celly - ry))
                return mm
            cur_m = min_myd_at(sx + dx, sy + dy)
            best_m = min_myd_at(sx + best_move[0], sy + best_move[1])
            if cur_m < best_m:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]