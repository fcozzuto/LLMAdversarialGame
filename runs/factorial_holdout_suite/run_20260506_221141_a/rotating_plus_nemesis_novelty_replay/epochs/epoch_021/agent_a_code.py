def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    def target_value(x, y, tx, ty):
        ds = abs(tx - x) + abs(ty - y)
        do = abs(tx - ox) + abs(ty - oy)
        # Prefer cells where we are closer to some resource than opponent, then closer overall.
        return (do - ds) * 100 - ds

    best = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        cell_best = -10**18
        for rx, ry in resources:
            v = target_value(nx, ny, rx, ry)
            if v > cell_best:
                cell_best = v
        # Small bias to move toward immediate gain
        if (nx, ny) in resources:
            cell_best += 1000
        if cell_best > best:
            best = cell_best
            best_move = [dx, dy]
    return best_move