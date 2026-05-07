def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # pick target where we are (or can become) relatively closer than opponent
    best = None
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    opp_sweep_bias = 0
    # sweep_rows tends to move along a coordinate; discourage targeting opponent's row/column
    # (uses simple heuristic based on distance in y)
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        adv = od - sd  # bigger is better
        row_col_pen = abs(ty - oy) * 0.05  # small but consistent
        center = abs(tx - cx) + abs(ty - cy) * 0.002
        key = (-(adv), sd + row_col_pen, center, tx, ty)
        if best is None or key < best[0]:
            best = (key, tx, ty)
    _, tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        # primary: reduce our distance; secondary: increase relative advantage (opponent farther)
        # tertiary: avoid stepping onto obstacle-adjacent cells
        adj_pen = 0
        if (nx + 1, ny) in obstacles or (nx - 1, ny) in obstacles or (nx, ny + 1) in obstacles or (nx, ny - 1) in obstacles:
            adj_pen = 0.03
        rel = (nod - nsd)
        key = (-rel, nsd, adj_pen, nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]