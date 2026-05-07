def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # If we can collect immediately, do it
    res_set = set(tuple(r) for r in resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    if not resources:
        return [0, 0]

    # Choose best resource by "advantage": (opp_dist - my_dist), then my_dist
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - md
        key = (adv, -md, - (rx == sx and ry == sy), -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Move one step that minimizes our distance to target; tie-break deterministically
    curd = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_key = (-10**9, 10**9, 0, 0)  # (improve, dist, step_pref, dir_index)
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        improve = curd - nd
        # Prefer moves that increase our lead against the target resource
        lead_now = cheb(ox, oy, tx, ty) - nd
        lead_key = lead_now
        step_pref = 1 if dx == 0 and dy == 0 else 0
        k = (improve, -nd, lead_key, -step_pref, -i)
        if k > best_key:
            best_key = k
            best_move = [dx, dy]

    return best_move