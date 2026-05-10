def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    # Pick resource where we beat opponent most in time-to-reach (Chebyshev).
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive means we are closer
        # tie-break: smaller self distance, then prefer higher (rx+ry)
        t = (lead, -sd, rx + ry)
        if best is None or t > best[0]:
            best = (t, rx, ry)
    _, tx, ty = best

    # Greedy move: among valid deltas, minimize our distance to target and maximize lead vs opponent.
    deltas = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0), (0, 0), (1, 0),
        (-1, 1), (0, 1), (1, 1)
    ]
    best_m = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        score = ((nod - nsd), -nsd, -abs(tx - (nx)) - abs(ty - (ny)), dx, dy)
        if best_m is None or score > best_m[0]:
            best_m = (score, dx, dy)

    if best_m is None:
        return [0, 0]
    return [best_m[1], best_m[2]]