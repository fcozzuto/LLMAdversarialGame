def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    free_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            free_moves.append((dx, dy, nx, ny))
    if not free_moves:
        return [0, 0]

    if resources:
        best = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            score = ds - (do * 0.3)
            cand = (score, ds, rx, ry)
            if best is None or cand < best:
                best = cand
        _, _, tx, ty = best
    else:
        tx, ty = ox, oy

    best_move = None
    for dx, dy, nx, ny in free_moves:
        d = dist(nx, ny, tx, ty)
        # Prefer staying still if equally good, otherwise smallest (dx,dy) lex deterministically.
        cand = (d, dx == 0 and dy == 0, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand
    return [best_move[2], best_move[3]]