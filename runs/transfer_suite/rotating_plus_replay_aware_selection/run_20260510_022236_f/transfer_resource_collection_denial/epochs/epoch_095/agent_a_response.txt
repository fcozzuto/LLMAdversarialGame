def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))

    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def opp_one_step_best(rx, ry):
        best = 10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = ox + dx, oy + dy
                if inb(nx, ny) and (nx, ny) not in obs:
                    d = cheb_dist(nx, ny, rx, ry)
                    if d < best: best = d
        return best if best != 10**9 else cheb_dist(ox, oy, rx, ry)

    best_cell = None
    best_score = None
    # Prefer not being on the row opponent is likely sweeping (same/adjacent y)
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = cheb_dist(sx, sy, rx, ry)
        do1 = opp_one_step_best(rx, ry)
        lead = do1 - ds
        row_pen = abs(ry - oy)  # higher penalty when close to opponent row
        # Prefer staying mobile: modest tie-breakers against long detours
        y_pref = -abs(ry - (h - 1) / 2.0)
        time_pref = -(ds + max(0, ds - tr // 2))
        score = (lead, -row_pen, time_pref, y_pref, -do1, -ds)
        if best_score is None or score > best_score:
            best_score = score
            best_cell = (rx, ry)

    if best_cell is None:
        return [0, 0]

    tx, ty = best_cell
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Simple obstacle-aware nudge: if diagonal step blocked, try axis moves deterministically
    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) not in obs:
        return [dx, dy]
    # Try horizontal then vertical then stay (deterministic order)
    nx, ny = sx + dx, sy
    if inb(nx, ny) and (nx, ny) not in obs: return [dx, 0]
    nx, ny = sx, sy + dy
    if inb(nx, ny) and (nx, ny) not in obs: return [0, dy]
    return [0, 0]