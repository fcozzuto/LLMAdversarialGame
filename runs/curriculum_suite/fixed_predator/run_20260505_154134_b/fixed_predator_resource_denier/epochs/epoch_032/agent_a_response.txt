def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource():
        # Prefer resources we can reach sooner than opponent; otherwise pick the most contested.
        best = None  # (priority, tie_key, (rx,ry))
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Priority: large when (do - ds) is big; secondarily prefer smaller ds;
            # then prefer closer/low-sum position for determinism.
            priority = (do - ds) * 1000 - ds
            tie_key = (ds, do, rx + ry, rx, ry)
            if best is None or (priority, -tie_key[0], -tie_key[1], -tie_key[2], -tie_key[3], -tie_key[4]) > (
                best[0][0], best[0][1], best[0][2], best[0][3], best[0][4], best[0][5]
            ):
                best = ((priority, -tie_key[0], -tie_key[1], -tie_key[2], -tie_key[3], -tie_key[4]), (rx, ry))
        if best is None:
            return (ox, oy)
        return best[1]

    tx, ty = best_resource()

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Main: get closer to target faster than opponent.
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        score = (do - ds) * 1000 - ds

        # Secondary: if near any resource, discourage moves that let opponent be strictly closer to that resource.
        # (Resource denial vs fixed_pool: maintain "intercept" pressure.)
        near_bonus = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            drs = cheb(nx, ny, rx, ry)
            if drs <= 1:
                dro = cheb(ox, oy, rx, ry)
                if dro < drs:
                    near_bonus -= 50
                elif dro == drs:
                    near_bonus += 5
                else:
                    near_bonus += 25
        score += near_bonus

        # Deterministic tie-break: prefer smaller dx, then smaller dy magnitude, then lexicographic.
        tie = (-abs(dx), -abs(dy), -dx, -dy)
        total = (score, tie)

        if total > (best_score, (-abs(best_move[0]), -abs(best_move[1]), -best_move[0], -best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]