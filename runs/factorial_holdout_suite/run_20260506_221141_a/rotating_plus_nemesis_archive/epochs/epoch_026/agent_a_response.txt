def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    res_list = observation.get("resources", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not inb(sx, sy):
        return [0, 0]

    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a contested target: prioritize resources where we are relatively closer than opponent.
    best_t = None
    for r in resources:
        my_d = man((sx, sy), r)
        op_d = man((ox, oy), r)
        cand = (my_d - op_d, my_d, -op_d, r[0], r[1])
        if best_t is None or cand < best_t[0]:
            best_t = (cand, r)
    target = best_t[1]

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = None

    # Also keep some awareness of opponent's nearest resource to "stall" it by moving away.
    opp_nearest = min(resources, key=lambda r: (man((ox, oy), r), r[0], r[1]))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d_t = man((nx, ny), target)
        op_d_t = man((ox, oy), target)
        my_gain = my_d_t
        op_gain = op_d_t

        # Encourage moving that increases opponent's relative position on the contested target
        # and slightly increases their distance to their own nearest resource.
        op_d_opp = man((ox, oy), opp_nearest)

        # Obstacle proximity penalty (avoid hugging obstacles)
        prox_pen = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            px, py = nx + ax, ny + ay
            if (px, py) in obs:
                prox_pen += 1

        score = (my_gain - op_gain, my_gain, -(op_d_opp), prox_pen, dx, dy)
        if best_move is None or score < best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]