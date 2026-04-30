def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # candidate moves in deterministic order
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def best_target(fromx, fromy):
        if not resources:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            return cx, cy
        best = None
        bestv = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = d2(fromx, fromy, rx, ry)
            do = d2(ox, oy, rx, ry)
            # prefer being sooner than opponent; slight bias to closer overall
            v = (do - ds) * 10 - ds
            if v > bestv:
                bestv = v
                best = (rx, ry)
        return best if best is not None else resources[0]

    tx, ty = best_target(sx, sy)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        # main heuristic: move closer to a contested target; also reduce opponent distance
        ds = d2(nx, ny, tx, ty)
        do = d2(nx, ny, ox, oy)
        opp_to_target = d2(ox, oy, tx, ty)
        # if opponent is likely to reach target first, prioritize cutting off near our closest contested point
        cutoff = 0.0
        if resources:
            # compute our advantage against the best resource from this position
            adv_best = -10**18
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                adv = d2(ox, oy, rx, ry) - d2(nx, ny, rx, ry)
                if adv > adv_best:
                    adv_best = adv
            cutoff = adv_best * 8.0

        # penalize getting too close to opponent to reduce direct contest losses
        score = (-ds * 6.0) + (opp_to_target - d2(nx, ny, tx, ty)) + (cutoff) + (-do * 0.2)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]