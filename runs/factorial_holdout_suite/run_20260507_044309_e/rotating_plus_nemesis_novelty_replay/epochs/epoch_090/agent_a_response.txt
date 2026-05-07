def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obs_raw = observation.get("obstacles") or []
    obstacles = obs_raw if isinstance(obs_raw, set) else set(tuple(p) for p in obs_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obstacles

    # pick best target by maximizing opponent advantage
    best = None
    best_delta = -10**18
    best_ds = 10**18
    best_rx = best_ry = 10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        delta = do - ds
        if (delta > best_delta) or (delta == best_delta and (ds < best_ds or (ds == best_ds and (rx < best_rx or (rx == best_rx and ry < best_ry))))):
            best_delta, best_ds, best_rx, best_ry = delta, ds, rx, ry
            best = (rx, ry)

    rx, ry = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy
        ns = cheb(nx, ny, rx, ry)
        no = cheb(ox, oy, rx, ry)
        score = (no - ns) * 1000 - ns
        # If target is already at/near, bias toward collecting it (distance 0)
        if ns == 0:
            score += 10**7
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]