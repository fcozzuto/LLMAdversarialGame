def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ox, oy = observation.get("opponent_position", [0, 0])

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    if not res:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_move = [0, 0]
    best = -10**18
    best_my = 10**18
    best_center = 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_best_gap = -10**18
        my_best_d = 10**18

        for rx, ry in res:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            gap = opp_d - my_d
            if gap > my_best_gap or (gap == my_best_gap and my_d < my_best_d):
                my_best_gap = gap
                my_best_d = my_d

        center_dist = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        score = my_best_gap * 1000 - my_best_d  # prioritize winning race, then closer
        if score > best or (score == best and (my_best_d < best_my or (my_best_d == best_my and center_dist < best_center))):
            best = score
            best_my = my_best_d
            best_center = center_dist
            best_move = [dx, dy]

    return best_move