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
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def cell_blocked(x, y):
        return (x, y) in obstacles

    best_target = None
    best_delta = -10**18
    best_ds = 10**18
    best_rx = best_ry = 10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        delta = do - ds
        if (delta > best_delta) or (delta == best_delta and (ds < best_ds or (ds == best_ds and (rx < best_rx or (rx == best_rx and ry < best_ry))))):
            best_delta = delta
            best_ds = ds
            best_target = (rx, ry)
            best_rx, best_ry = rx, ry

    rx, ry = best_target

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if cell_blocked(nx, ny):
            continue
        ns = cheb(nx, ny, rx, ry)
        no = cheb(ox, oy, rx, ry)
        advantage = no - ns
        # tie-break: prefer smaller ns, then closer lexicographically to target
        cand.append((-(advantage), ns, abs(rx - nx) + abs(ry - ny), rx - nx, ry - ny, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    return [cand[0][5], cand[0][6]]