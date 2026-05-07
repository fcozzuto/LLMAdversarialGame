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

    res = [tuple(r) for r in resources]
    # Opponent likely target: nearest (tie -> deterministic)
    opp_idx = min(range(len(res)), key=lambda i: (md(ox, oy, res[i][0], res[i][1]), i))
    opp_t = res[opp_idx]
    my_start_d_opp_t = md(sx, sy, opp_t[0], opp_t[1])
    opp_start_d_opp_t = md(ox, oy, opp_t[0], opp_t[1])

    best_move = valid[0]
    best_score = None

    for m in valid:
        nx, ny = m[2], m[3]
        my_d_opp_t = md(nx, ny, opp_t[0], opp_t[1])
        # Primary: deny by reaching opponent's target no later than they do
        deny_primary = 0
        if my_d_opp_t <= opp_start_d_opp_t:
            deny_primary = 1000 - my_d_opp_t  # prefer closer while denying
        else:
            deny_primary = -(my_d_opp_t - opp_start_d_opp_t)  # least harmful

        # Secondary: choose a resource we can beat better than opponent
        # Score = our_dist - opp_dist (prefer negative), tie by our_dist.
        best_gap = 10**9
        best_our = 10**9
        for i in range(len(res)):
            rx, ry = res[i]
            d_me = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            gap = d_me - d_op
            if gap < best_gap or (gap == best_gap and (d_me < best_our)):
                best_gap = gap
                best_our = d_me

        # Combine; ensure determinism with tie-break on move index
        score = (deny_primary, -best_gap, -best_our, valid.index(m))
        if best_score is None or score > best_score:
            best_score = score
            best_move = m

    return [best_move[0], best_move[1]]