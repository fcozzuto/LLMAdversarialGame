def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def resource_value(px, py, rx, ry):
        myd = cheb(px, py, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if myd == 0:
            return 10_000
        # Prefer resources I'm closer to (opd-myd), then shorter my distance.
        # Slightly discourage giving opponent a too-easy race.
        race = opd - myd
        return (1000 * race) - (25 * myd) - (3 * (myd > opd))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if not resources:
            # If no resources, drift to maximize distance from opponent (deterministic).
            sc = cheb(nx, ny, ox, oy)
        else:
            # Choose the best target from this next position.
            sc = max(resource_value(nx, ny, rx, ry) for rx, ry in resources)
            # Add small tie-break on immediate advantage vs opponent.
            sc += cheb(nx, ny, ox, oy) * 0.01
        key = (-sc, dx, dy)
        if key < (-best_score, best_move[0], best_move[1]):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]