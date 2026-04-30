def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, dict):
            x = r.get("x", r.get("pos", [None, None])[0])
            y = r.get("y", r.get("pos", [None, None])[1])
        else:
            x, y = r[0], r[1]
        if x is not None and y is not None:
            resources.append((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best = moves[0]
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_opp = cheb(nx, ny, ox, oy)
        d_corner = min(cheb(nx, ny, cx, cy) for cx, cy in corners)
        if resources:
            d_res = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            v = -d_res + 0.12 * d_opp - 0.01 * d_corner
        else:
            v = 2.0 * (-d_opp) - 0.01 * d_corner
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]