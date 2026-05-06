def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    cx_bias = -(abs(sx - (w - 1) / 2) + abs(sy - (h - 1) / 2)) * 0.001
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Advantage: for the same resource, prefer moves that make us closer than opponent.
        adv_best = -10**18
        mind = 10**18
        for rx, ry in resources:
            ds = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)
            adv = do - ds
            if adv > adv_best:
                adv_best = adv
            if ds < mind:
                mind = ds

        # Tie-breakers: prefer smaller distance to nearest resource and slightly toward center.
        center_bias = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.001
        score = adv_best * 1000 - mind + center_bias + cx_bias
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move