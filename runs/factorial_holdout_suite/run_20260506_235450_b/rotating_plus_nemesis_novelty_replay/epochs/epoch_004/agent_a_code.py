def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda p: (dist2(sx, sy, p[0], p[1]), -dist2(ox, oy, p[0], p[1]), p[0], p[1]))
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            key = (dist2(nx, ny, tx, ty), dist2(nx, ny, ox, oy), nx, ny)
            if best is None or key < best: best = key; best_move = [dx, dy]
        return best_move if best is not None else [0, 0]

    # Target resource with advantage over opponent: prefer smaller (d_self - d_opp).
    best_overall = None
    best_move = [0, 0]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: continue
        # If we can collect immediately, do it.
        if [nx, ny] in resources:
            return [dx, dy]
        cur_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles: continue
            ds = dist2(nx, ny, rx, ry)
            do = dist2(ox, oy, rx, ry)
            # Encourage winning contests: smaller ds-do; tiebreak by smaller ds.
            key = (ds - do, ds, rx, ry)
            if cur_best is None or key < cur_best: cur_best = key
        if cur_best is None: continue
        # Also consider opponent closeness in general (avoid moving into their capture radius).
        opp_general = dist2(nx, ny, ox, oy)
        key2 = (cur_best[0], cur_best[1], opp_general, nx, ny)
        if best_overall is None or key2 < best_overall:
            best_overall = key2
            best_move = [dx, dy]
    return best_move if best_overall is not None else [0, 0]