def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def near_obst(x, y):
        c = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in obst:
                c += 1
        return c

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            # Prefer resources we can reach first; penalize resources too close to opponent.
            v = 0
            v -= near_obst(nx, ny) * 0.7
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Only relative matters; also encourage moving closer overall.
                rel = do - ds
                v += rel * 2.2 - ds * 0.35
                # If we are already on it, win this turn's objective heavily.
                if nx == rx and ny == ry:
                    v += 1e6
            # Small preference for increasing distance from opponent while contesting resources
            v += cheb(nx, ny, ox, oy) * 0.06
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            best = (0, 0)
        return [int(best[0]), int(best[1])]

    # No resources: drift away from opponent and avoid corners if it would trap us.
    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        v = cheb(nx, ny, ox, oy) * 1.2 - near_obst(nx, ny) * 0.8
        # Also slightly prefer moving toward the center to reduce being cornered.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        v += (1.0 / (1.0 + manh(nx, ny, cx, cy))) * 0.3
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]