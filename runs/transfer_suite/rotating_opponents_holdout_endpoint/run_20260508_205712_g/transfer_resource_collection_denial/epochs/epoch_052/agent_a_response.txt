def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    def clamp_inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            key = (myd - od, myd, rx + ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx = 0 if ox > sx else W - 1
        ty = 0 if oy > sy else H - 1

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        myd2 = md(nx, ny, tx, ty)
        od2 = md(nx, ny, ox, oy)

        on_target = 1 if (nx, ny) == (tx, ty) else 0
        myd_cur = md(sx, sy, tx, ty)
        od_cur = md(sx, sy, ox, oy)
        opp_closer_to_target = 1 if (md(ox, oy, tx, ty) - md(nx, ny, tx, ty)) >= 0 else 0

        score = (
            myd2,
            -od2,
            -on_target,
            (myd2 - myd_cur),
            -opp_closer_to_target
        )
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]