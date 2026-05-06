def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources_sorted = resources[:]
    resources_sorted.sort(key=lambda t: (t[0], t[1]))

    phase = int(observation.get("turn_index", 0) or 0) % 3
    opp_weight = 0.85 if phase == 0 else (0.65 if phase == 1 else 0.75)
    edge_weight = 0.08

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        # Value: lower is better. Prefer resources we're relatively closer to than opponent,
        # while avoiding tight proximity to opponent and discouraging edge chasing.
        local_best = 10**18
        for rx, ry in resources_sorted:
            d_self = abs(nx - rx) + abs(ny - ry)
            d_opp = abs(nx - ox) + abs(ny - oy)
            # Balance: go for resource where our distance is good vs opponent's distance to it.
            d_opp_to_res = abs(nx - ox) + abs(ny - oy)  # proxy for "opponent pressure near our move"
            rel = d_self - opp_weight * (abs(rx - ox) + abs(ry - oy))
            prox = abs(nx - ox) + abs(ny - oy)
            val = rel + 0.35 * prox + 0.12 * d_opp_to_res
            if val < local_best:
                local_best = val

        edge_pen = edge_weight * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny) == 0)
        center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        center_pen = 0.03 * center

        # Deterministic tie-break: smallest (dx,dy) lex among equal best.
        total = local_best + edge_pen + center_pen
        if best_val is None or total < best_val or (total == best_val and (dx, dy) < best_move):
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]