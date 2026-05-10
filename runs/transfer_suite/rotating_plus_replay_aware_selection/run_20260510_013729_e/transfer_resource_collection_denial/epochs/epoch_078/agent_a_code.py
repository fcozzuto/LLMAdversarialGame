def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    if not resources:
        return [0, 0]

    # Predict opponent as greedy toward their nearest resource (with obstacle-aware step)
    tx0, ty0 = resources[0]
    bestd = man(ox, oy, tx0, ty0)
    for rx, ry in resources[1:]:
        d = man(ox, oy, rx, ry)
        if d < bestd:
            bestd = d
            tx0, ty0 = rx, ry

    def step_toward(ax, ay, tx, ty):
        best = (ax, ay, 10**9)
        for mdx, mdy in moves:
            nx, ny = ax + mdx, ay + mdy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < best[2]:
                best = (nx, ny, d)
        return best[0], best[1]

    nxo, nyo = step_toward(ox, oy, tx0, ty0)

    best_move = (0, 0, -10**9, 10**9)  # mdx, mdy, score, our_best_dist
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue

        # Our closest resource
        our_best = 10**9
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if d < our_best:
                our_best = d

        # Opponent closest resource after their predicted step
        opp_best = 10**9
        for rx, ry in resources:
            d = man(nxo, nyo, rx, ry)
            if d < opp_best:
                opp_best = d

        # Prefer moves that put us closer than opponent; slight deterministic bias by turn parity
        score = (opp_best - our_best) * 1000 - our_best
        if (observation["turn_index"] % 2) == 1:
            score += (1 if our_best == opp_best else 0)

        if score > best_move[2] or (score == best_move[2] and our_best < best_move[3]):
            best_move = (mdx, mdy, score, our_best)

    return [int(best_move[0]), int(best_move[1])]