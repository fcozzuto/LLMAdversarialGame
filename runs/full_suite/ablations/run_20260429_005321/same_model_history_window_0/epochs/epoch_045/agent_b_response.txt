def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = 0, 0 if (sx + sy) <= (w - 1 - sx + h - 1 - sy) else (w - 1, h - 1)
    else:
        best = None
        # Choose a resource we are relatively closer to than the opponent.
        for rx, ry in resources:
            sd = cd(sx, sy, rx, ry)
            od = cd(ox, oy, rx, ry)
            eff = sd - 0.35 * od
            if best is None or eff < best[0] or (eff == best[0] and (sd < best[1] or (sd == best[1] and (rx, ry) < best[2]))):
                best = (eff, sd, (rx, ry))
        tx, ty = best[2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = [0, 0]
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cd(nx, ny, tx, ty)
        od = cd(nx, ny, ox, oy)
        # Prefer approaching target; slightly avoid getting too close to opponent.
        val = -d * 10 + od
        if d == 0:
            val += 1000
        # Deterministic tie-break by move order (dirs order already fixed).
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]