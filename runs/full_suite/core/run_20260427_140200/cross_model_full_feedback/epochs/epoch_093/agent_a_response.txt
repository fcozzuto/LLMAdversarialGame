def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    mx, my = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    mx, my, ox, oy = int(mx), int(my), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Greedy chase (deterministic) if no targets
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if blocked(nx, ny):
                continue
            sc = -manh(nx, ny, ox, oy)
            if sc > best[2]:
                best = (dx, dy, sc)
        return [best[0], best[1]]

    # Pick a target deterministically: max advantage among resources at our next-step reach (approx)
    # Advantage = opp_dist - my_dist (higher means we are closer/easier to secure)
    best_t = resources[0]
    best_a = -10**9
    for tx, ty in resources:
        a = manh(ox, oy, tx, ty) - manh(mx, my, tx, ty)
        # Slight tie-break toward resources closer to us (and away from being adjacent to opponent)
        a2 = a * 100 - manh(mx, my, tx, ty) - manh(ox, oy, tx, ty) // 4
        if a2 > best_a:
            best_a = a2
            best_t = (tx, ty)
    tx, ty = best_t

    # Score candidate moves: maximize immediate advantage gain + reduce distance to target
    # Also discourage stepping into obstacles/out-of-bounds; candidate list already filters.
    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if blocked(nx, ny):
            continue
        myd = manh(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)
        base_adv = opd - myd  # higher better
        # Encourage blocking: if we move closer to any resource and opponent not, reward a bit
        if resources:
            near_bonus = 0
            for rx, ry in resources:
                if (rx, ry) == (tx, ty):
                    continue
                if myd <= manh(nx, ny, rx, ry):
                    continue
                # small deterministic bonus for approaching other resources too
                near_bonus += (manh(nx, ny, rx, ry) - manh(ox, oy, rx, ry))
            base_adv += near_bonus // 3
        # Avoid proximity to opponent if tie
        opp_prox = -max(0, 5 - manh(nx, ny, ox, oy))
        sc = base_adv * 10 - myd + opp_prox
        if sc > best[2]:
            best = (dx, dy, sc)

    return [int(best[0]), int(best[1])]