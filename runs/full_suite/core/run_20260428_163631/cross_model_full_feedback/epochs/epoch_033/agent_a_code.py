def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    if resources:
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            md = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < md:
                    md = d
            key = (md, cheb(nx, ny, ox, oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
    else:
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            key = (-cheb(nx, ny, ox, oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)

    return [int(best[0]), int(best[1])]