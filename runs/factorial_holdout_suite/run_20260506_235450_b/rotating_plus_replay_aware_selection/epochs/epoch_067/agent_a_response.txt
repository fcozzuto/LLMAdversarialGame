def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {(int(p[0]), int(p[1])) for p in obs_list if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best_target = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        self_d = cheb((sx, sy), (rx, ry))
        opp_d = cheb((ox, oy), (rx, ry))
        margin = opp_d - self_d  # bigger => we are ahead
        key = (-(margin), self_d, rx + ry, rx, ry)  # minimize negative margin => maximize margin; then speed
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    direct_dx = 0 if tx == sx else (1 if tx > sx else -1)
    direct_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Prefer the direct step if legal; otherwise choose best legal move by distance-to-target and "race" to next resource.
    preferred = None
    for dx, dy, nx, ny in legal:
        if dx == direct_dx and dy == direct_dy:
            preferred = (dx, dy, nx, ny)
            break
    if preferred is not None:
        return [preferred[0], preferred[1]]

    best = None
    best_move_key = None
    for dx, dy, nx, ny in legal:
        self_d = cheb((nx, ny), (tx, ty))
        opp_d = cheb((ox, oy), (tx, ty))
        key = (-(opp_d - self_d), self_d, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]