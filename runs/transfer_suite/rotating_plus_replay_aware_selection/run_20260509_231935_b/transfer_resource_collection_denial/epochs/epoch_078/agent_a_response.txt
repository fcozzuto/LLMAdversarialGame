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
            res.append((int(p[0]), int(p[1])))
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_min = 10**9
        opp_min = 10**9
        on_res = 0
        for rx, ry in res:
            d_my = cheb(nx, ny, rx, ry)
            if d_my < my_min:
                my_min = d_my
            d_opp = cheb(ox, oy, rx, ry)
            if d_opp < opp_min:
                opp_min = d_opp
            if nx == rx and ny == ry:
                on_res = 1

        if on_res:
            score = 10**6 - my_min
        else:
            score = (-my_min * 10) + (opp_min * 3)

        # Slight tie-break toward moving closer to center to avoid oscillation
        cx = (w - 1) // 2
        cy = (h - 1) // 2
        center_bias = -(cheb(nx, ny, cx, cy))
        score += center_bias * 0.05

        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]