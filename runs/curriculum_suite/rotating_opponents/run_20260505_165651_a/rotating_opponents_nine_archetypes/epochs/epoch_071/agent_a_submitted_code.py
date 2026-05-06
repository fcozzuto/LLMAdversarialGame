def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def man(a, b, c, d):
        t = a - c
        if t < 0:
            t = -t
        u = b - d
        if u < 0:
            u = -u
        return t + u

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if resources:
        tr = []
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                x, y = r[0], r[1]
                if inb(x, y) and (x, y) not in obs:
                    tr.append((x, y))
    else:
        tr = []

    best_dx, best_dy = 0, 0
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        if tr:
            dres = min(manh(nx, ny, rx, ry) for rx, ry in tr)
            dopp = cheb(nx, ny, ox, oy)
            v = (-dres) + 0.15 * (dopp) - 0.01 * man(nx, ny, cx, cy)
        else:
            dcent = man(nx, ny, cx, cy)
            dopp = cheb(nx, ny, ox, oy)
            v = (-dcent) + 0.2 * (dopp)
        if v > bestv:
            bestv = v
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]