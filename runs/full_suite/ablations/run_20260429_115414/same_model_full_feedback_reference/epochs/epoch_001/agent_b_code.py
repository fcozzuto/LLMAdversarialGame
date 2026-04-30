def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    tx, ty = ox, oy
    best = None
    for r in resources:
        rx, ry = r[0], r[1]
        myd = abs(sx - rx) + abs(sy - ry)
        opd = abs(ox - rx) + abs(oy - ry)
        key = (myd - opd, myd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is not None:
        tx, ty = best[1]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (10**9, 0, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        myd = abs(nx - tx) + abs(ny - ty)
        opd = abs(ox - tx) + abs(oy - ty)
        adv = opd - myd
        score = (myd, -adv, dx, dy)
        if score < (best_move[0], best_move[1], best_move[2], best_move[3]):
            best_move = (score[0], score[1], score[2], score[3])

    dx, dy = best_move[2], best_move[3]
    if not inside(sx + dx, sy + dy) or (sx + dx, sy + dy) in obs:
        return [0, 0]
    return [int(dx), int(dy)]