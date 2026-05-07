def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Pick target deterministically.
    best = None
    best_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        reach_first = 1 if myd <= opd else 0
        # Strongly punish giving opponent a faster grab.
        score = reach_first * 1000 + (opd - myd) * 8 - myd * 2
        # Mild obstacle-adjacent penalty near target to avoid dead-ends.
        pen = 0
        for adx, ady in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = rx + adx, ry + ady
            if (nx, ny) in obstacles:
                pen += 1
        score -= pen
        # Deterministic tie-break: lower myd, then lexicographic.
        key = (score, -myd, -opd, rx, ry)
        if best is None or key > best_score:
            best = (rx, ry)
            best_score = key

    tx, ty = best
    # Decide move by evaluating the 9 possible deltas.
    best_mv = [0, 0]
    best_mscore = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer reducing our cheb to target; if close, prioritize capture race.
            mscore = (opd - myd) * 10 - myd * 3
            # If move also improves proximity to any immediate resource, add small bonus.
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                if cheb(nx, ny, rx, ry) < cheb(sx, sy, rx, ry):
                    mscore += 2
            # Avoid stepping into cells adjacent to many obstacles (deterministic shaping).
            adj = 0
            for adx, ady in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (nx + adx, ny + ady) in obstacles:
                    adj += 1
            mscore -= adj
            tieb = (mscore, -myd, opd, dx, dy)
            if best_mscore is None or tieb > best_mscore:
                best_mscore = tieb
                best_mv = [dx, dy]

    return [int(best_mv[0]), int(best_mv[1])]