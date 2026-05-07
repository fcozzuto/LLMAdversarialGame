def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if (rx, ry) in obs:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd, -((rx + 3 * ry) % (w + h)))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r if best_r is not None else (sx, sy)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Prefer moves that keep/extend lead toward the same target; small tie-breakers for stability.
        score = (-(d_to - cheb(sx, sy, tx, ty)), -d_to, (nx - ox) * 0.01 + (ny - oy) * 0.01 + ((nx + ny) % 2) * 0.001)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_score is None:
        return [0, 0]
    return best_move