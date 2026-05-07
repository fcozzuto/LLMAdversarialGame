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

    # Pick target: maximize capture advantage now.
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        row_bias = abs(ry - oy)  # tends to move away from opponent along y
        parity_bias = -(((ry - oy) & 1) + ((rx - sx) & 1))  # small tie-breaker
        key = (adv, -sd, row_bias, parity_bias)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    cur_d = cheb(sx, sy, tx, ty)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        nd = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        adv = opp_d - nd
        # Prefer moves that improve distance, and more strongly when already close.
        improvement = cur_d - nd
        tie = -(abs(ry - oy) if False else 0)  # keep deterministic structure
        val = (adv, improvement, -nd, -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)), tie)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move