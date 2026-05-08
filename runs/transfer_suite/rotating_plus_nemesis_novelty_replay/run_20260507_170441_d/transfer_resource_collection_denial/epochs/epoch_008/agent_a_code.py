def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Select target where we are relatively closer than opponent (tie -> nearer)
    tx, ty = resources[0][0], resources[0][1]
    best = -10**30
    for rx, ry in resources:
        myd = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        gain = opd - myd
        tie = -(myd)
        key = (gain, tie)
        if key[0] > best or (key[0] == best and (rx, ry) < (tx, ty)):
            best = key[0]
            tx, ty = rx, ry

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Small obstacle penalty: avoid stepping onto obstacle and heavily avoid immediate-near cells
    best_score = -10**30
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        # penalty if next to obstacle (including diagonal adjacency)
        near = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if (ax, ay) in obst:
                    near = 1
                    break
            if near:
                break
        myd = d2(nx, ny, tx, ty)
        opd = d2(nx, ny, ox, oy)
        # primary: reduce distance to target, secondary: keep distance from opponent
        score = -myd + 0.02 * opd - (500.0 if near else 0.0)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]