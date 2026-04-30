def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (cheb(ox, oy, c[0], c[1]), -c[0], -c[1]))
        if (sx, sy) == (tx, ty):
            return [0, 0]
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach no later, then maximize our lead; otherwise minimal disadvantage
            key = (0 if myd <= opd else 1, myd - opd, myd, -rx, -ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
        if (sx, sy) == (tx, ty):
            return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            d = cheb(nx, ny, tx, ty)
            # break ties by keeping distance from opponent (deny pressure) and then coords
            deny = cheb(ox, oy, nx, ny)
            cand.append((d, -deny, dx, dy, nx, ny))
    if not cand:
        return [0, 0]
    cand.sort()
    _, _, dx, dy, _, _ = cand[0]
    return [int(dx), int(dy)]