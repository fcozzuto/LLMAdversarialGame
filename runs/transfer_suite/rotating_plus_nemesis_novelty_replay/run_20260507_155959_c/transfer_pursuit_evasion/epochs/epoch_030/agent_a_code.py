def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    res = observation.get("resources", None) or []
    resources = [tuple(p) for p in res]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dO = man(sx, sy, nx, ny) if (nx, ny) == (ox, oy) else man(nx, ny, ox, oy)
        if resources:
            dR = min(man(nx, ny, rx, ry) for rx, ry in resources)
        else:
            dR = 0
        close = man(nx, ny, ox, oy) <= 2
        v = (dO - dR) if close else (-dR + 0.2 * dO)
        key = (v, -dO, dR, dx, dy)
        if best is None or key > bestv:
            bestv = key
            best = [dx, dy]
    if best is not None:
        return best
    return [0, 0] if inb(sx, sy) else [1, 0] if inb(sx + 1, sy) else [-1, 0] if inb(sx - 1, sy) else [0, 1] if inb(sx, sy + 1) else [0, -1] if inb(sx, sy - 1) else [0, 0]