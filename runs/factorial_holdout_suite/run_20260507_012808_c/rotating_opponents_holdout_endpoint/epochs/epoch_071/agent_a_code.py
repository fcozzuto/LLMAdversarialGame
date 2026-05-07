def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target we are likely to secure first; prefer bigger lead, then closer.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd
        # Secondary nudge: prefer targets more "in front" of us relative to opponent side
        toward = (rx - sx) * (rx - ox) + (ry - sy) * (ry - oy)
        key = (lead, -sd, toward)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    # Score candidate moves by how much they reduce our distance to the target and open space.
    def free_neighbors(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    c += 1
        return c

    bestm = None
    bestmk = None
    curd = cheb(sx, sy, tx, ty)
    for dx, dy, nx, ny in moves:
        nd = cheb(nx, ny, tx, ty)
        progress = curd - nd
        threat = cheb(ox, oy, tx, ty) - cheb(ox, oy, nx, ny)
        key = (progress, free_neighbors(nx, ny), threat, -abs((tx - nx)) - abs((ty - ny)))
        if bestmk is None or key > bestmk:
            bestmk = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]