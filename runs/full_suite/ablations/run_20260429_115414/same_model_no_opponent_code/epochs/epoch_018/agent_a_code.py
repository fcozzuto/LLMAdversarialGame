def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles if 0 <= int(x) < w and 0 <= int(y) < h)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    rs = []
    for x, y in resources:
        x, y = int(x), int(y)
        if free(x, y):
            rs.append((x, y))
    if not rs:
        return [0, 0]

    best = None
    best_score = -10**18
    for x, y in rs:
        md = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer resources we can reach reasonably and for which we're closer than opponent.
        score = (od - md) * 200 - md
        # Mild preference for resources not too far from center to reduce wandering.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= int(abs(x - cx) + abs(y - cy))
        if score > best_score:
            best_score = score
            best = (x, y)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: closer to target, then prefer moving in direction that reduces our distance to opponent (disrupt).
    best_move = (0, 0)
    best_d = 10**9
    best_dis = 10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        dis = cheb(nx, ny, ox, oy)
        if d < best_d or (d == best_d and dis < best_dis) or (d == best_d and dis == best_dis and (dx, dy) < best_move):
            best_d = d
            best_dis = dis
            best_move = (dx, dy)

    dx, dy = best_move
    if dx == 0 and dy == 0 and not free(sx, sy):
        return [0, 0]
    return [int(dx), int(dy)]