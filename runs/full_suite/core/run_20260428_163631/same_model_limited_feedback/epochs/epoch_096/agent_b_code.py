def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dx else (dy if dy >= 0 else -dy)

    def dist(a, b):
        dx = sx - a
        dy = sy - b
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dfrom(px, py, tx, ty):
        dx = px - tx
        dy = py - ty
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    if resources:
        best = None
        for rx, ry in resources:
            ds = dfrom(sx, sy, rx, ry)
            do = dfrom(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer than opponent.
            key = ds - 0.6 * do + 0.05 * (abs(sx - rx) + abs(sy - ry) == 0)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**9, 0, 0)
    for dx, dy in deltas:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        dt = dfrom(nx, ny, tx, ty) if resources else dfrom(nx, ny, int(round(tx)), int(round(ty)))
        dop = dfrom(nx, ny, ox, oy)
        # Safety/denial: avoid getting too close to opponent unless it also helps reach target.
        safety = 0.25 * max(0, 2 - dop)
        val = dt + safety
        if val < best_move[0] or (val == best_move[0] and (dx, dy) < (best_move[1], best_move[2])):
            best_move = (val, dx, dy)
    return [int(best_move[1]), int(best_move[2])]