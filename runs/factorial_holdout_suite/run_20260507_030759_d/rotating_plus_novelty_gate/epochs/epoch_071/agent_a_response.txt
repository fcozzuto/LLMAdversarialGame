def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = [(p[0], p[1]) for p in (observation.get("resources", []) or []) if isinstance(p, (list, tuple)) and len(p) >= 2]
    if (sx, sy) in set(resources):
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal or not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    mypos = (sx, sy)
    opppos = (ox, oy)

    # Pick a resource where we are ahead vs opponent (opp_d - my_d is larger).
    best_r = None
    best_key = None
    for r in resources:
        myd = md(mypos, r)
        opd = md(opppos, r)
        key = (opd - myd, -myd, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key, best_r = key, r
    tx, ty = best_r

    # Then pick the move that gets us closest to that target, while not making it easier for opponent.
    best_move = None
    best_mv_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd_next = md((nx, ny), (tx, ty))
        opd_next = md(opppos, (tx, ty))
        # Prefer: smaller my distance; if tied, larger opponent advantage margin (opd_next - myd_next).
        key = (myd_next, -(opd_next - myd_next), dx, dy)
        if best_mv_key is None or key < best_mv_key:
            best_mv_key, best_move = key, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]