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
    for p in obstacles or []:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_to = 10**9
        opp_to = 10**9
        my_adv = -10**9
        near_res = 10**9
        near_op = 10**9

        for rx, ry in res:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if md < my_to:
                my_to = md
            if od < opp_to:
                opp_to = od
            adv = od - md
            if adv > my_adv:
                my_adv = adv
            d1 = cheb(nx, ny, rx, ry)
            if d1 < near_res:
                near_res = d1
            d2 = cheb(ox, oy, rx, ry)
            if d2 < near_op:
                near_op = d2

        center_bias = -abs(nx - cx) - abs(ny - cy)
        # Prefer immediate capture/close to a resource, and maximize distance advantage vs opponent on that resource.
        move_score = (my_adv, -near_res, opp_to, center_bias)
        if best is None or move_score > best:
            best = move_score
            best_move = [dx, dy]

    return best_move