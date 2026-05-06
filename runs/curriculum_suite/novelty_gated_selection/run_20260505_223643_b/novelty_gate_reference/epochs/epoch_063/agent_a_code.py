def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    if (sx, sy) in resources or not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target: beat the opponent while avoiding their likely sweeping row.
    def cell_score(t):
        sd = man((sx, sy), t)
        od = man((ox, oy), t)
        row_pen = 0 if t[1] != oy else 6  # avoid same row as opponent
        col_pen = 0 if t[0] != ox else 2  # slight avoid same column
        # Prefer cells where we're closer, but with stable tie-breaking.
        return (row_pen + col_pen - (od - sd), sd, t[0], t[1])

    target = min(resources, key=cell_score)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**9, 0, 0)
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in resources:
            return [dx, dy]
        nd = man((nx, ny), target)
        od = man((ox, oy), target)
        # Maintain progress toward target; add anti-sweep bias by discouraging landing on opponent row.
        sweep_bias = 0 if ny != oy else 3
        val = (nd + sweep_bias, -((od - nd) if od is not None else 0), nx, ny)
        if val < best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]