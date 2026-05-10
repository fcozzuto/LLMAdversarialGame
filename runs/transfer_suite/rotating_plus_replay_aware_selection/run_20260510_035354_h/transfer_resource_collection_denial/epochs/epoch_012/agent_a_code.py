def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target(x0, y0):
        best = None
        for rx, ry in resources:
            myd = kdist(x0, y0, rx, ry)
            opd = kdist(ox, oy, rx, ry)
            key = (opd - myd, -myd, -(myd - opd), -rx, -ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        return best[1], best[2]

    if not resources:
        return [0, 0]

    tx, ty = best_target(sx, sy)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    cand = []
    for dx, dy, nx, ny in moves:
        ntx, nty = tx, ty
        # If we are already on/at target cell, just hold best future position toward closest winning resource
        if (sx, sy) != (tx, ty):
            ntx, nty = best_target(nx, ny)
        myd = kdist(nx, ny, ntx, nty)
        opd = kdist(ox, oy, ntx, nty)
        cand.append(((opd - myd, -myd, -kdist(ox, oy, nx, ny)), dx, dy))
    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]