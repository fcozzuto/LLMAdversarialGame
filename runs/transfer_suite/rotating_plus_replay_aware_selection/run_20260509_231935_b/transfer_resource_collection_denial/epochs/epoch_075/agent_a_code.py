def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))
    if not res:
        return [0, 0]
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_min = 10**9
        opp_min = 10**9
        my_second = 10**9
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            if d < my_min:
                my_second, my_min = my_min, d
            elif d < my_second:
                my_second = d
            od = cheb(ox, oy, rx, ry)
            if od < opp_min:
                opp_min = od

        dist_adv = opp_min - my_min  # bigger is better (we're closer to some resource than opponent)
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # Small tie-break to prefer continued progress (avoid pure dithering)
        progress = -(my_second - my_min)

        val = dist_adv * 1000 + center + progress
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move