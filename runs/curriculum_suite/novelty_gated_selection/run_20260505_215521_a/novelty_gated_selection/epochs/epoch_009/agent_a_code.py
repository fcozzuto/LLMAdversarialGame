def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_res_dist(x, y):
        if not resources:
            return 10**9
        m = 10**9
        for tx, ty in resources:
            d = man(x, y, tx, ty)
            if d < m:
                m = d
        return m

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_d0 = best_res_dist(ox, oy)
    best = None
    for dx, dy, nx, ny in moves:
        self_d = best_res_dist(nx, ny)
        opp_d = best_res_dist(ox, oy)
        advantage = (opp_d - self_d) if resources else 0
        dist_opp = man(nx, ny, ox, oy)
        center = abs(nx - cx) + abs(ny - cy)
        on_res = 1 if (nx, ny) in set(resources) else 0
        score = advantage * 1000 + on_res * 500 + dist_opp * 2 - center
        key = (score, on_res, dist_opp, -center, -abs(dx) - abs(dy))
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    return best[1]