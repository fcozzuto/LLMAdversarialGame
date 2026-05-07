def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    resources = observation.get("resources", []) or []
    res = set((r[0], r[1]) for r in resources)

    if (sx, sy) in res and (sx, sy) not in obstacles:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def best_target(x, y):
        if not res:
            return None
        # Deterministic: if multiple at same distance, tie-break by coordinates
        bx, by = None, None
        bd = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            d = abs(rx - x) + abs(ry - y)
            if bd is None or d < bd or (d == bd and (rx, ry) < (bx, by)):
                bd = d
                bx, by = rx, ry
        return bx, by

    target = best_target(sx, sy)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if target is None:
            # No resources: head away from opponent slightly, prefer reducing distance to border corner
            d_opp = abs(nx - ox) + abs(ny - oy)
            border_score = (nx, ny)  # deterministic
            val = (-d_opp, -border_score[0], -border_score[1])
        else:
            tx, ty = target
            d_self = abs(tx - nx) + abs(ty - ny)
            d_opp = abs(tx - ox) + abs(ty - oy)
            # Prefer moves that reduce our distance to target; if tie, prefer increasing opponent distance
            val = (d_self, -d_opp, nx, ny)
        if best is None or val < best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]