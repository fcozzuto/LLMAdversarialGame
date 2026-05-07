def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)
    if not res:
        return [0, 0]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    tr = observation.get("turns_remaining", 0)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def sign(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    # Prefer resources we can secure (reach no later than opponent), otherwise take the quickest.
    best = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Large weight on winning the race; secondary on finishing earlier (turns horizon helps).
        secure = 1 if ds <= do else 0
        horizon = 0 if tr is None else tr
        key = (secure, do - ds, -ds, -((horizon - ds) if horizon else 0), rx, ry)
        if best is None or key > best_key:
            best, best_key = (rx, ry), key

    if best is None:
        return [0, 0]
    tx, ty = best

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If horizon allows, bias toward shorter time to collection; else bias toward race advantage.
    def value(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        secure = 1 if ns <= no else 0
        finish = -(ns)
        race = (no - ns)
        if tr and tr > 0:
            hurry = -abs(tr - ns)
            return (secure * 10**6) + race * 1000 + finish * 10 + hurry
        return (secure * 10**6) + race * 1000 + finish * 10

    best_d = None
    best_v = None
    # Tie-break deterministically by movement order around desired direction.
    ddx = sign(tx - sx)
    ddy = sign(ty - sy)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        v = value(nx, ny)
        tie = (-(abs(dx - ddx) + abs(dy - ddy)), -abs(dx) - abs(dy))
        if best_d is None or v > best_v or (v == best_v and tie > best_tie):
            best_d = (dx, dy)
            best_v = v
            best_tie = tie

    if best_d is None:
        return [0, 0]
    return [int(best_d[0]), int(best_d[1])]