def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def clamp_inb(x, y):
        return 0 <= x < W and 0 <= y < H
    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx = 0 if ox > sx else W - 1
        ty = 0 if oy > sy else H - 1
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            key = (sd - od, sd, -rx - ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        myd = md(nx, ny, tx, ty)
        opd = md(nx, ny, ox, oy)
        # Prefer decreasing distance to target and not giving opponent too good access
        val = (myd, md(nx, ny, tx, ty) - md(ox, oy, tx, ty), opd)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]