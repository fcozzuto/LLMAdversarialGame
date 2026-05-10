def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        ds = cheb_dist(sx, sy, rx, ry)
        do = cheb_dist(ox, oy, rx, ry)
        # Primary: maximize advantage (opponent slower). Secondary: minimize our distance.
        key = (do - ds, -ds)
        if best is None or key > best[0]:
            best = (key, (rx, ry))

    (rx, ry) = best[1]
    dx = 0
    if rx > sx: dx = 1
    elif rx < sx: dx = -1
    dy = 0
    if ry > sy: dy = 1
    elif ry < sy: dy = -1

    nx, ny = sx + dx, sy + dy
    if not inb(nx, ny) or (nx, ny) in obs:
        # Try axis-aligned alternative deterministically
        if dx != 0:
            for ax, ay in [(dx, 0), (0, dy), (0, 0)]:
                tx, ty = sx + ax, sy + ay
                if inb(tx, ty) and (tx, ty) not in obs:
                    return [ax, ay]
        for ax, ay in [(0, dy), (dx, 0), (0, 0)]:
            tx, ty = sx + ax, sy + ay
            if inb(tx, ty) and (tx, ty) not in obs:
                return [ax, ay]
        return [0, 0]
    return [dx, dy]