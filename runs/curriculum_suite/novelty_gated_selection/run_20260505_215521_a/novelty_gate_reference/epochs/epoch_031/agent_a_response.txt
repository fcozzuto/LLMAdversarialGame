def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    resources = observation.get("resources", []) or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                res_list.append((x, y))
    if not res_list:
        return [0, 0]

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def risk(x, y):
        rr = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obs_set:
                    rr += 1
        return rr

    def cell_score(cell):
        cx, cy = cell
        sd = abs(cx - sx) + abs(cy - sy)
        od = abs(cx - ox) + abs(cy - oy)
        rsk = risk(cx, cy)
        diag_bias = abs((cx - sx) - (cy - sy))  # prefer balanced diagonal progress
        # Lower is better: prioritize capturing quickly while staying ahead of opponent,
        # and avoid obstacle-adjacent cells.
        return (sd - 0.85 * od, rsk, diag_bias, sd)

    target = min(res_list, key=cell_score)

    tx, ty = target
    pref_dx = 0 if tx == sx else (1 if tx > sx else -1)
    pref_dy = 0 if ty == sy else (1 if ty > sy else -1)

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        # Evaluate move by how it improves target approach, with slight "intercept" pressure.
        move_sd = abs(tx - nx) + abs(ty - ny)
        move_od = abs(tx - ox) + abs(ty - oy)
        v = (move_sd - 0.85 * move_od, risk(nx, ny), abs(dx - pref_dx) + abs(dy - pref_dy), nx, ny)
        if best_val is None or v < best_val:
            best_val = v
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]