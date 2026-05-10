def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            resources.append((int(r[0]), int(r[1])))
        except Exception:
            pass

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; if tied, go closer overall
            key = (do - ds, -ds, -(abs(rx - ox) + abs(ry - oy)), -abs(rx - sx) - abs(ry - sy))
            if best is None or key > best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        # Head to parity-aligned corner to avoid getting stuck
        if ((ox + oy) & 1) == 0:
            tx, ty = 0, 0
        else:
            tx, ty = w - 1, h - 1

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            moves.append((dx, dy))

    best_m = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        hit = (nx, ny) in obstacles
        new_ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        lead = do - new_ds  # positive means we get closer than opponent to target
        # Penalize obstacle landing strongly; otherwise greedy toward target with lead preservation
        key = (lead, -new_ds, -((hit + 0) * 1000), -abs(nx - ox) - abs(ny - oy), -((dx == 0 and dy == 0) * 0.5))
        if best_key is None or key > best_key:
            best_key = key
            best_m = [dx, dy]

    return best_m