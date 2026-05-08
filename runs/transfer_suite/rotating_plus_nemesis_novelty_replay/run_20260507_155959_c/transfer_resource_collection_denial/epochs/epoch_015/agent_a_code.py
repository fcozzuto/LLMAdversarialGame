def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(int(r[0]), int(r[1])) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    best = None
    bestkey = None
    for rx, ry in res:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Gain if we can arrive sooner; slight preference for nearer overall and fewer Manhattan steps.
        key = (do - ds, -ds, -((rx + ry) % 7), rx, ry)
        if bestkey is None or key > bestkey:
            bestkey = key
            best = (rx, ry)

    tx, ty = best
    opp_d = md(ox, oy, tx, ty)
    self_d = md(sx, sy, tx, ty)

    # Greedy one-step improvement with deterministic scoring.
    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) == (tx, ty):
            score = 10**12
        else:
            d_self = md(nx, ny, tx, ty)
            # Prefer moves that keep advantage or create it; also avoid giving opponent a faster route to the target.
            score = 0
            score += (opp_d - d_self) * 1000
            score += (-d_self) * 3
            # Additional pressure: if we can deny any resource within one step, do it.
            deny = 0
            for rx, ry in res:
                if md(nx, ny, rx, ry) == 0 and (md(ox, oy, rx, ry) >= 1):
                    deny = 1
                    break
            score += 5000 * deny
            # Slight anti-stall unless already best.
            if (dx, dy) == (0, 0) and not (self_d <= 2 and opp_d >= self_d):
                score -= 5

        key = (score, -abs(dx), -abs(dy), dx, dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]