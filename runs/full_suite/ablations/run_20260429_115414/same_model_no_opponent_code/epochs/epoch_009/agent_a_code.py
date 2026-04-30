def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = [(int(x), int(y)) for x, y in resources]
    if not res:
        tx, ty = (w - 1 - ox), (h - 1 - oy)
    else:
        best = None
        for rx, ry in res:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Pick most favorable (reach sooner). Break ties by being closer to me, then farther from opponent.
            key = (md - od, md, -od, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        _, tx, ty = best

    oppd = cheb(sx, sy, ox, oy)
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_to_t = cheb(nx, ny, tx, ty)
        my_to_o = cheb(nx, ny, ox, oy)
        # If I'm behind on the chosen target, prioritize making approach while also increasing separation.
        # If I'm ahead, prioritize fast capture (reduce distance) and avoid getting too close to opponent.
        behind = cheb(sx, sy, tx, ty) - cheb(ox, oy, tx, ty)
        if behind > 0:
            score = (0, my_to_t, -my_to_o, abs(nx - tx) + abs(ny - ty), dx, dy)
        else:
            score = (1, my_to_t, oppd - my_to_o, -my_to_o, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]