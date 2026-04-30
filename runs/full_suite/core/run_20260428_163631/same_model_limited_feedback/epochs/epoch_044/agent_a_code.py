def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, dict):
            x, y = p.get("x"), p.get("y")
        else:
            x, y = p
        if x is not None and y is not None:
            obstacles.add((int(x), int(y)))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, dict):
            x, y = r.get("x"), r.get("y")
        else:
            x, y = r
        if x is not None and y is not None:
            resources.append((int(x), int(y)))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            v = -cheb(nx, ny, int(cx), int(cy)) - 0.3 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best
    best_r = None
    best_need = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # prefer resources where we are closer or at least not worse; tie-break by smaller ds
        need = (do < ds, ds, rx, ry)
        if best_r is None or need < best_need:
            best_r = (rx, ry)
            best_need = need
    rx, ry = best_r
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        v = -cheb(nx, ny, rx, ry)
        # discourage stepping close to opponent unless we are much closer to the target
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        v -= 0.15 * cheb(nx, ny, ox, oy) * (1.0 if ds >= do else 0.4)
        if (nx, ny) == (rx, ry):
            v += 10**6
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best