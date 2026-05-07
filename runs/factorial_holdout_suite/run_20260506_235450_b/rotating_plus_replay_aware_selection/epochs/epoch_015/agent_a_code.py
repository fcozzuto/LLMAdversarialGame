def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    legal = []
    for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    for dx, dy, nx, ny in legal:
        # Evaluate next position by best contested advantage among remaining resources.
        best_adv = -10**9
        best_self = 10**9
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self
            if adv > best_adv or (adv == best_adv and d_self < best_self):
                best_adv = adv
                best_self = d_self
        # Tie-break: prefer moving toward lower self distance, then toward resources in same quadrant as opponent (helps vs sweep).
        quad_bias = 0
        if ox >= sx: quad_bias += 1
        if oy >= sy: quad_bias += 1
        key = (best_adv, -best_self, quad_bias, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]