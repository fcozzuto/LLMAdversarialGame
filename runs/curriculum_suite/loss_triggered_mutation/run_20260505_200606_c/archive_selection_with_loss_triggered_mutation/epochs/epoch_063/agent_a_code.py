def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a resource I can contest: minimize (my_dist - opp_dist); tie-break by absolute closeness.
    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            key = (myd - opd, myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
        contest_backing = (best_key[0] > 0)  # I'm farther than opponent -> play more defensive
    else:
        # No resources: head toward a plausible interception line (mid between corners).
        tx, ty = (w - 1 + 0) // 2, (h - 1 + 0) // 2
        contest_backing = True

    cur_my = man(sx, sy, tx, ty)
    cur_opp = man(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        myd = man(nx, ny, tx, ty)
        opd = man(nx, ny, ox, oy)

        # Core: reduce my distance to target, but also avoid letting opponent reach it sooner.
        new_my_to_t = myd
        new_opp_to_t = man(ox, oy, tx, ty)  # static relative to move; keep term simple/deterministic

        # When behind, weight strongly to increase opponent separation.
        d_my = new_my_to_t - cur_my
        d_opp_sep = man(nx, ny, ox, oy) - man(sx, sy, ox, oy)

        # Slightly prefer moves that don't step "toward" opponent in Manhattan sense.
        toward_opp = man(nx, ny, ox, oy) - man(sx, sy, ox, oy)

        score = (10 * d_my) + (3 * toward_opp) + (-0.5 * d_opp_sep)
        if contest_backing:
            score += 8 * toward_opp  # prioritize staying away when I'm contesting from behind

        # Tie-break: avoid dead-ends by preferring cells with more available neighboring squares.
        if score is not None:
            free_n = 0
            for adx, ady in moves:
                ax, ay = nx + adx, ny + ady
                if inb(ax, ay) and (ax, ay) not in obstacles:
                    free_n += 1
            score += -0.01 * (7 - free_n)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]