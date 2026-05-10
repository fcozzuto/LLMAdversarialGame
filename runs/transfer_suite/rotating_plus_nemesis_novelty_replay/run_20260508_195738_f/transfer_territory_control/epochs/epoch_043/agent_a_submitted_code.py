def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    x, y = sp[0], sp[1]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells", []) or []
    uc = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ux, uy = int(p[0]), int(p[1])
            if 0 <= ux < w and 0 <= uy < h and (ux, uy) not in obs:
                uc.append((ux, uy))

    tx, ty = int(op[0]), int(op[1])
    if uc:
        tx, ty = min(uc, key=lambda p: abs(p[0] - x) + abs(p[1] - y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    oppx, oppy = int(op[0]), int(op[1])

    best = (0, 0)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        adj_opp = 1 if abs(nx - oppx) <= 1 and abs(ny - oppy) <= 1 and (nx, ny) != (opx, oppy) else 0
        s = -d + 3 * adj_opp
        if s > best_s:
            best_s = s
            best = (dx, dy)
    return [best[0], best[1]]