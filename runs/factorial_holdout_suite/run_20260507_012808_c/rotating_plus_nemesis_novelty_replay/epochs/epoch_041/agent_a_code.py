def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return abs(dx) + abs(dy)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        # deterministic: drift toward the nearest free corner
        corners = [(0, 0), (0, h-1), (w-1, 0), (w-1, h-1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            d = md(sx, sy, cx, cy) + 0.01 * md(ox, oy, cx, cy)
            if best is None or d < best[0]:
                best = (d, cx, cy)
        if best is None:
            return [0, 0]
        tx, ty = best[1], best[2]
        best_step = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            score = md(nx, ny, tx, ty)
            if score < best_step[0]:
                best_step = (score, dx, dy)
        return [int(best_step[1]), int(best_step[2])]

    # pick resource we can likely reach first
    best_r = None
    best_val = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # prefer resources where we are closer than opponent; otherwise still move toward good ones
        val = (od - sd) * 10 - sd
        if best_val is None or val > best_val:
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r

    # choose step that most reduces distance to target, with secondary tie-break: increase our advantage
    best_step = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        sd_new = md(nx, ny, tx, ty)
        # advantage after moving (heuristic)
        od_cur = md(ox, oy, tx, ty)
        adv = (od_cur - sd_new)  # higher better
        key = (sd_new, -adv, abs(nx - tx) + abs(ny - ty))
        if best_step is None or key < best_step[0]:
            best_step = (key, dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[1]), int(best_step[2])]