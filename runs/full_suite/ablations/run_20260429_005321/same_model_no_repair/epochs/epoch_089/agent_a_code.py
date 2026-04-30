def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            key = (cheb(nx, ny, cx, cy), -cheb(nx, ny, ox, oy), 0 if (dx == 0 and dy == 0) else 1)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    best_target = None
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer targets we are closer to; break ties by choosing nearer and then "deterministic" by coord.
        key = (md - od, md, rx, ry)
        if best_target is None or key < best_target[0]:
            best_target = (key, rx, ry)
    _, tx, ty = best_target

    best_move = None
    for dx, dy, nx, ny in legal:
        md = cheb(nx, ny, tx, ty)
        od = cheb(nx, ny, ox, oy)
        # Move to reduce target distance; also keep distance from opponent if close tie.
        key = (md, -od, 0 if (dx == 0 and dy == 0) else 1, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)
    return [best_move[1], best_move[2]]