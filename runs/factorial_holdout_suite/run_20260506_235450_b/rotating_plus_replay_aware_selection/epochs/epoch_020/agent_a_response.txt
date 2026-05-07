def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Opponent denier: prioritize resources we can reach first; if none, minimize their lead.
    best = None  # (value, tie_d, dx, dy)
    for dx, dy, nx, ny in legal:
        best_here = -10**9
        tie_d = 10**9
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            diff = do - ds  # positive => we are closer
            if diff > 0:
                v = 1000 + diff * 10 - ds  # strongly prefer winning races
            elif diff == 0:
                v = 500 - ds
            else:
                v = - (abs(diff) * 20 + ds)  # penalize resources opponent is closer to
            if v > best_here or (v == best_here and ds < tie_d):
                best_here = v
                tie_d = ds
        cand = (best_here, tie_d, dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[2]), int(best[3])]