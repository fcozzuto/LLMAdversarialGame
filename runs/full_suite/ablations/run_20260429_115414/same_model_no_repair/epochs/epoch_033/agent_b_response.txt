def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None  # (gain, mydist, rx, ry)
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in blocked:
                continue
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gain = od - md  # prefer resources we're closer to
            cand = (gain, -md, rx, ry)
            if best is None or cand > best:
                best = cand
        if best is None:
            tx, ty = w // 2, h // 2
        else:
            _, _, tx, ty = best

    # Greedy step toward (tx, ty) with obstacle avoidance and deterministic tie-break.
    best_move = None  # (md2, od2, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        md2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        cand = (md2, -od2, dx, dy)  # closer to target; prefer positions that keep opponent farther
        if best_move is None or cand < best_move:
            best_move = cand

    if best_move is None:
        return [0, 0]
    return [int(best_move[2]), int(best_move[3])]