def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy
    resources = observation.get("resources", []) or []
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]
    if not resources:
        tx, ty = w // 2, h // 2
        best = min(valid, key=lambda m: (md(m[2], m[3], tx, ty), valid.index(m)))
        return [best[0], best[1]]

    # Opponent likely target: their nearest resource (tie -> lowest index for determinism)
    res = [tuple(r) for r in resources]
    opp_idx = min(range(len(res)), key=lambda i: (md(ox, oy, res[i][0], res[i][1]), i))
    opp_t = res[opp_idx]
    d_opp_to_opp_t = md(ox, oy, opp_t[0], opp_t[1])

    # Decide: contest opponent's target if we can reach no later; else go for best resource we can beat.
    # Scoring evaluates next step with a deterministic contest-aware heuristic.
    best_move = None; best_val = None
    for j, (dx, dy, nx, ny) in enumerate(valid):
        my_to_opp_t = md(nx, ny, opp_t[0], opp_t[1])
        contest = 0
        if my_to_opp_t <= d_opp_to_opp_t:
            contest = 1000 - (my_to_opp_t - d_opp_to_opp_t)  # higher if equal/earlier

        # Find best resource for us considering we might still lose to opponent there.
        # Approx "we win" if our distance <= opponent distance for that resource.
        best_gain = -10**9
        for i, (rx, ry) in enumerate(res):
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # prefer winning or getting closer to our best; discourage resources opponent can beat
            if myd <= opd:
                gain = 2000 - (myd - opd) - i * 0.001
            else:
                gain = - (myd - opd) - i * 0.001
            if gain > best_gain:
                best_gain = gain

        # Additional small bias: reduce distance to nearest resource to avoid dithering.
        nearest = min(md(nx, ny, rx, ry) for (rx, ry) in res)
        val = (-best_gain, -contest, nearest, j)  # lexicographic via tuples through inversion on first two
        if best_val is None or val < best_val:
            best_val = val; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]