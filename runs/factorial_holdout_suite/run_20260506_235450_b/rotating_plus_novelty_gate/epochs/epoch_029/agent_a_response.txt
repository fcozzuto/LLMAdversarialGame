def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # our advantage if positive
        row_bias = abs(ry - oy)  # prefer farther rows from opponent
        parity_bias = -((ry - oy) & 1)
        key = (adv, -sd, row_bias, parity_bias)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                d_to = cheb(nx, ny, tx, ty)
                d_opp = cheb(nx, ny, ox, oy)
                # prefer getting closer, also slightly prefer being farther from opponent
                score = (d_to, -d_opp, abs(tx - nx) + abs(ty - ny), 0 if (dx == 0 and dy == 0) else 1)
                moves.append((score, dx, dy))
    if not moves:
        return [0, 0]

    moves.sort()
    _, dx, dy = moves[0]
    return [dx, dy]