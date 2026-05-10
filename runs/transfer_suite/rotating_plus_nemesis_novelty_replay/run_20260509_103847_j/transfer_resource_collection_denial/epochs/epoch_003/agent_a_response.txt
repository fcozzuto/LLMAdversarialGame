def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        key = (myd - opd, myd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    best_move = (0, 0)
    best_key = (10**9, 10**9, 10**9)

    # Candidate moves include staying still.
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            myd_new = dist(nx, ny, tx, ty)
            opd_new = dist(ox, oy, tx, ty)
            # Primary: keep/extend advantage (smaller myd-opd).
            # Secondary: get closer to target.
            # Tertiary: deterministic tie-break by move preference.
            adv = myd_new - opd_new
            pref = (abs(dx) + abs(dy), (dx, dy))
            key = (adv, myd_new, pref[0])
            if key < best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]