def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist_manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    # Choose a resource: first prefer ones we can reach no later than opponent; otherwise best deny (opp closer).
    best = None
    for rx, ry in resources:
        myd = dist_manh(sx, sy, rx, ry)
        opd = dist_manh(ox, oy, rx, ry)
        can_secure = 1 if myd <= opd else 0
        # Score: prefer secure; within secure prefer smaller myd; else deny by maximizing (opd - myd).
        score = (0 if can_secure else 1, myd if can_secure else -(opd - myd), dist_manh(rx, ry, w - 1, h - 1), rx, ry)
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    # Move: if we can secure now (or close), minimize our distance to target and avoid getting worse than opponent.
    # If opponent is closer, maximize the gap (opp - me) after the move and slightly press toward target.
    secure_now = dist_manh(sx, sy, tx, ty) <= dist_manh(ox, oy, tx, ty)

    best_move = None
    best_mscore = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = dist_manh(nx, ny, tx, ty)
        opd2 = dist_manh(ox, oy, tx, ty)
        gap = opd2 - myd2
        # Tie-break: also consider moving closer to opponent when we are losing to increase contest pressure.
        oppd2 = dist_manh(nx, ny, ox, oy)
        if secure_now:
            # Prioritize reaching target quickly; ensure we don't fall behind too much.
            mscore = (0, myd2, -gap, oppd2, dx, dy)
        else:
            # Prioritize widening gap; if can't, move toward target anyway.
            mscore = (1, -gap, myd2, oppd2, dx, dy)
        if best_mscore is None or mscore < best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]