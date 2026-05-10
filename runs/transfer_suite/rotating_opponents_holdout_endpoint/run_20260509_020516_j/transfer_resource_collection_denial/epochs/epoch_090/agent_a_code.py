def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    if not resources:
        return [0, 0]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = [0, 0]
    best_score = -10**18

    # One-step evaluation: maximize immediate capture, then win races against opponent.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            mypos = (nx, ny)
            score = 0

            if mypos in res_set:
                score += 10**6  # immediate collection

            # Resource race pressure: reward resources where we are closer than opponent.
            win_bonus = 0
            close_penalty = 0
            for rx, ry in resources:
                rpos = (rx, ry)
                dm = mdist(mypos, rpos)
                do = mdist((ox, oy), rpos)
                if dm == 0:
                    continue
                # Bigger when we're closer; damped when far.
                delta = do - dm  # positive means we are closer
                weight = 1.0 / (1 + dm)
                if delta > 0:
                    win_bonus += delta * weight
                # slight preference to approach some resource even if not strictly winning
                close_penalty += (dm / (1 + dm)) * 0.15
            score += win_bonus - close_penalty

            # Avoid getting too close to opponent only when that doesn't help capture
            dOpp = mdist(mypos, (ox, oy))
            score += (dOpp * 0.01)

            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move