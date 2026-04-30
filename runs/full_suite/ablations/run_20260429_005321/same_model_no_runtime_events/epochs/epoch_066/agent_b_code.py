def choose_move(observation):
    w = int(observation.get("grid_width") or 0) or 8
    h = int(observation.get("grid_height") or 0) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in dirs:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def score_to(tx, ty):
        ax = sx - tx
        if ax < 0: ax = -ax
        ay = sy - ty
        if ay < 0: ay = -ay
        return ax if ax >= ay else ay

    best = (10**9, 10**9, None)
    target_list = resources if resources else [(ox, oy)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_t = 10**9
        for tx, ty in target_list:
            best_t = min(best_t, (abs(nx - tx) if abs(nx - tx) >= abs(ny - ty) else abs(ny - ty)))
        opp_dist = abs(nx - ox)
        if opp_dist < abs(ny - oy):
            opp_dist = abs(ny - oy)
        # Prefer getting closer to resources; if none, prefer moving away from opponent (or less toward).
        primary = best_t
        secondary = opp_dist
        cand = (primary, -secondary, (dx, dy))
        if cand[0] < best[0] or (cand[0] == best[0] and cand[1] < best[1]):
            best = cand

    if best[2] is None:
        return [0, 0]
    return [best[2][0], best[2][1]]