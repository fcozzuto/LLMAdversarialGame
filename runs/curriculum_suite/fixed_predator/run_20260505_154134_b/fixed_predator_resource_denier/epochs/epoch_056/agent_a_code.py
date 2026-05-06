def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    cheb = lambda ax, ay, bx, by: (abs(ax - bx) if abs(ax - bx) > abs(ay - by) else abs(ay - by))

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best = None

    if resources:
        targets = []
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            targets.append((adv, -sd, rx, ry))
        if targets:
            targets.sort(reverse=True)
            adv0, nsd0, tx, ty = targets[0]
        else:
            tx, ty = w // 2, h // 2
    else:
        tx, ty = w // 2, h // 2

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist_to = cheb(nx, ny, tx, ty)
        dist_opp = cheb(nx, ny, ox, oy)
        advantage = dist_opp - dist_to  # prefer being closer than opponent to the target
        score = (advantage, -dist_to)
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move