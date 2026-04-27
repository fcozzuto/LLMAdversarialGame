def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs_list) if obs_list else set()
    res_list = observation.get("resources", [])
    resources = [(r[0], r[1]) for r in res_list] if res_list else []

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if resources:
        # pick best resource by advantage vs opponent
        best_r = resources[0]
        best_key = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            key = (do - ds, -ds, -(rx * 3 + ry))
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        rx, ry = best_r
        best_move = (0, 0)
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            ns = man(nx, ny, rx, ry)
            no = man(nx, ny, ox, oy)
            val = (-ns, no)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # no resources: move to increase distance from opponent; otherwise toward center
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist_opp = man(nx, ny, ox, oy)
        dist_center = man(nx, ny, cx, cy)
        key = (dist_opp, -dist_center, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]