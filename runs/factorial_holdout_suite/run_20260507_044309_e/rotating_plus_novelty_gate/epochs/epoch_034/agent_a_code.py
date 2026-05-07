def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy

    resources = observation.get("resources") or []
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None; best_key = None
        for i, (dx, dy, nx, ny) in enumerate(valid):
            d = md(nx, ny, tx, ty)
            key = (d, i)
            if best_key is None or key < best_key:
                best_key = key; best = (dx, dy)
        return [best[0], best[1]]

    # Race heuristic: prioritize resources where we are closer than opponent; otherwise pick best opportunity.
    best_move = (0, 0); best_key = None
    for i, (dx, dy, nx, ny) in enumerate(valid):
        my_best = 10**9
        opp_best = 10**9
        lead_best = -10**9
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)
            if myd < my_best: my_best = myd
            if oppd < opp_best: opp_best = oppd
            lead = oppd - myd
            if lead > lead_best: lead_best = lead
        # Tie-break: prefer immediate pickup, then largest lead, then closer overall
        immediate = 0 if any((rx == nx and ry == ny) for rx, ry in resources) else 1
        key = (immediate, -lead_best, my_best, i)
        if best_key is None or key < best_key:
            best_key = key; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]