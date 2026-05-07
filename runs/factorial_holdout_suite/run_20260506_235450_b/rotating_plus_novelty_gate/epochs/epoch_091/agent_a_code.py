def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                rs.append((x, y))
    if not rs:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # pick best target by maximizing (opponent_ETA - self_ETA), then closeness tie-break
    best_t = rs[0]
    best_adv = -10**9
    best_eta = 10**9
    for tx, ty in rs:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and ds < best_eta):
            best_adv = adv
            best_eta = ds
            best_t = (tx, ty)
    tx, ty = best_t

    # choose move that best improves ETA advantage toward target; also avoid stepping farther when adv is tight
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        adv = no - ns
        # small tie-break toward movement that reduces self_ETA
        val = adv * 1000 - ns
        # if target not advantaged, prefer moving closer to any resource not necessarily best-t
        if best_adv <= 0:
            val += -min(cheb(nx, ny, rx, ry) for rx, ry in rs)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]