def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obst = set((x, y) for x, y in obstacles)
    res = set((x, y) for x, y in resources)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_resource(px, py):
        best = None
        bestd = 10**9
        for rx, ry in res:
            d = abs(rx - px) + abs(ry - py)
            if d < bestd:
                bestd = d
                best = (rx, ry)
        return best, bestd

    def best_move(fromx, fromy):
        tgt, _ = nearest_resource(fromx, fromy)
        if tgt is None:
            return (fromx, fromy)
        tx, ty = tgt
        best = (fromx, fromy)
        bestScore = -10**18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = fromx + dx, fromy + dy
                if not inb(nx, ny) or (nx, ny) in obst:
                    continue
                score = - (abs(tx - nx) + abs(ty - ny))
                if (nx, ny) in res:
                    score += 1000
                score += -0.1 * (abs(ox - nx) + abs(oy - ny))
                if score > bestScore:
                    bestScore = score
                    best = (nx, ny)
        return best

    my_tgt, _ = nearest_resource(sx, sy)
    op_next = best_move(ox, oy)
    opnx, opny = op_next

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    bestMove = (0, 0)
    bestVal = -10**18
    for dx, dy, nx, ny in candidates:
        val = 0
        if (nx, ny) in res:
            val += 2000
        tgt, d = nearest_resource(nx, ny)
        if tgt is not None:
            val += -1.5 * d
            tx, ty = tgt
            # Intercept/deny: prefer moves that put you closer to the target than opponent would be.
            od = abs(tx - opnx) + abs(ty - opny)
            val += 1.0 * (od - d)
        # Safety: keep some distance from opponent if contesting.
        dist_op = abs(opnx - nx) + abs(opny - ny)
        val += 0.05 * dist_op
        # If opponent is near your nearest target, bias toward it.
        if my_tgt is not None:
            mt = my_tgt
            md = abs(mt[0] - nx) + abs(mt[1] - ny)
            omd = abs(mt[0] - opnx) + abs(mt[1] - opny)
            val += 0.8 * (omd - md)
        if val > bestVal:
            bestVal = val
            bestMove = (dx, dy)

    return [int(bestMove[0]), int(bestMove[1])]