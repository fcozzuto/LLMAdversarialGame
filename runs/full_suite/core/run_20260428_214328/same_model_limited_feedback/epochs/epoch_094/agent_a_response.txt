def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        target = (w // 2, h // 2)
    else:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            du = abs(rx - sx) + abs(ry - sy)
            dv = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we can get sooner; penalize those opponent is close to
            val = (dv - du) * 3 - du
            # Tie-break deterministically by coordinates
            tie = rx * 10 + ry
            cand = (val, du, tie, rx, ry)
            if best is None or cand > best:
                best = cand
        target = (best[3], best[4]) if best else (w // 2, h // 2)

    tx, ty = target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            # Heuristic: approach target, but don't let opponent get strictly better to it
            myd = abs(tx - nx) + abs(ty - ny)
            oppd = abs(tx - ox) + abs(ty - oy)
            # Estimate if opponent is likely to pressure: reduce score if opponent is closer already
            pressure = 0
            if resources:
                # check if target is still present and compare
                # (deterministic lightweight approximation)
                pressure = max(0, oppd - (myd)) * 0.1
            center_bias = -0.01 * ((nx - w / 2) ** 2 + (ny - h / 2) ** 2)
            # deterministic tie-breaker
            tieb = nx * 100 + ny * 10 + (dx + 1) * 3 + (dy + 1)
            moves.append((( -myd - pressure + center_bias), tieb, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True)
    return [int(moves[0][2]), int(moves[0][3])]