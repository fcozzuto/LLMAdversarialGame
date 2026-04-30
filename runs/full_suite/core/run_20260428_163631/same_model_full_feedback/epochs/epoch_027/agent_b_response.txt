def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = man(nx, ny, tx, ty)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Relative-closest heuristic: minimize (our_dist_to_nearest - opp_dist_to_nearest)
    # plus a small bias to reduce our distance.
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        our_near = 10**9
        opp_near = 10**9
        for rx, ry in resources:
            d1 = man(nx, ny, rx, ry)
            if d1 < our_near:
                our_near = d1
            d2 = man(ox, oy, rx, ry)
            if d2 < opp_near:
                opp_near = d2
        advantage_gap = our_near - opp_near  # smaller is better
        move_bias = man(nx, ny, ox, oy) * 0.01  # slight preference away/toward neutrality
        key = (advantage_gap, our_near + move_bias, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]