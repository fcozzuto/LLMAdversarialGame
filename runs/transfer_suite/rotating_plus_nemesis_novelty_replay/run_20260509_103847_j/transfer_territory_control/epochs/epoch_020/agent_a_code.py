def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                targets.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if targets:
        tx, ty = min(targets, key=lambda t: (man(sx, sy, t[0], t[1]), t[0], t[1]))
        best = None
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -man(nx, ny, tx, ty) - 0.01 * man(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    valid = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]
    dx, dy = min(valid, key=lambda d: (man(sx + d[0], sy + d[1], ox, oy), d[0], d[1]))
    return [dx, dy]