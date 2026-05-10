def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Race score: for best resource, how much closer we are than opponent (positive is good).
        # Small preference for shorter distance to reduce dithering.
        my_best = -10**18
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            race = opd - myd
            bonus = 2 if (nx, ny) == (rx, ry) else 0
            cand = race + bonus - 0.01 * myd
            if cand > my_best:
                my_best = cand

        # Mild "interference" term: don't give up if opponent is already closer to all resources.
        opp_nearest = min(cheb(ox, oy, int(r[0]), int(r[1])) for r in resources)
        my_nearest = min(cheb(nx, ny, int(r[0]), int(r[1])) for r in resources)
        interference = 0.05 * (opp_nearest - my_nearest)
        score = my_best + interference

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break: prefer moves with smaller distance to the most favorable resource (computed for current move).
            tx = ty = None
            bestd = 10**9
            for r in resources:
                rx, ry = int(r[0]), int(r[1])
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                race = opd - myd
                bonus = 2 if (nx, ny) == (rx, ry) else 0
                if race + bonus - 0.01 * myd >= my_best - 1e-12:
                    if myd < bestd:
                        bestd = myd
                        tx, ty = rx, ry
            cur_tx = ty  # dummy to keep deterministic variables local
            if cheb(nx, ny, tx if tx is not None else sx, ty if ty is not None else sy) < cheb(sx + best_move[0], sy + best_move[1], tx if tx is not None else sx, ty if ty is not None else sy):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]