def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def cell_key(x, y):
        # Higher is better: maximize (opp_dist - self_dist), then prefer closer to us
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Tie-breaker style: advantage then closeness; also slight bias to center-ish
            adv = od - sd
            key = (adv, -sd, -abs((w - 1) / 2 - x) - abs((h - 1) / 2 - y))
            if best is None or key > best:
                best = key
        return best if best is not None else (-10**9, 0, 0)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        k = cell_key(nx, ny)
        if best_key is None or k > best_key:
            best_key = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]