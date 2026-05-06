def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # Deterministic drift to opponent when no resources
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if inside(nx, ny) else [0, 0]

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_best = 10**9
        opp_best = 10**9
        diff_best = 10**9
        nearest_to_me = 10**9
        nearest_tiebreak = (10**9, 10**9)
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            dgap = myd - opd  # negative means I'm closer / likely to arrive first
            if myd < nearest_to_me or (myd == nearest_to_me and (rx, ry) < nearest_tiebreak):
                nearest_to_me = myd
                nearest_tiebreak = (rx, ry)
            if dgap < diff_best or (dgap == diff_best and (myd, opd, rx, ry) < (my_best, opp_best, nearest_tiebreak[0], nearest_tiebreak[1])):
                diff_best = dgap
                my_best = myd
                opp_best = opd
        key = (diff_best, my_best, -opp_best, nearest_to_me, nearest_tiebreak[0], nearest_tiebreak[1], dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]