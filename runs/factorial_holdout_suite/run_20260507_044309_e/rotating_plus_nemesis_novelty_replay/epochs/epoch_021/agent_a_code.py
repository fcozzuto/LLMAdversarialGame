def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    options = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in options:
        nx = sx + dx
        ny = sy + dy
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1

        move_best = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            if nx == rx and ny == ry:
                adv = 10000.0
            else:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                adv = (od - sd)
                if ry == oy:
                    adv += 2.5
                adv += -0.08 * sd
                if od == 0 and sd != 0:
                    adv += -3.0  # don't rush if opponent already on it
            if adv > move_best:
                move_best = adv

        # secondary: don't drift too far from engagement line
        drift = cheb(nx, ny, ox, oy)
        score = move_best - 0.02 * drift

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]