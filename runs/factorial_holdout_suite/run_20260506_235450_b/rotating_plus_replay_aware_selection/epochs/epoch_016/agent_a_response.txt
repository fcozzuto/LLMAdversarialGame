def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Resource-denier aware: prioritize resources we can match/beat; otherwise take the one they are closest to and race it.
        can_take = 1 if d_self <= d_opp else 0
        # Small secondary preference toward closer/equal goals to avoid dithering.
        key = (can_take, d_opp - d_self, -d_self, -(rx + 31 * ry))
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Choose the move that best reduces distance to the target; if tied, pick the one that increases opponent distance to it (denial).
    best_m = None
    for dx, dy, nx, ny in legal:
        d1 = cheb(nx, ny, tx, ty)
        d2 = cheb(ox, oy, tx, ty)
        # approximate denial: prefer moves that also keep us away from stepping onto opponent's immediate neighborhood.
        opp_near = cheb(nx, ny, ox, oy) <= 1
        key = (-d1, (1 if d2 >= cheb(ox, oy, tx, ty) else 0), (0 if opp_near else 1))
        if best_m is None or key > best_m[0]:
            best_m = (key, dx, dy)
    return [int(best_m[1]), int(best_m[2])]