def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_good(x, y):
        if not inside(x, y) or (x, y) in obstacles:
            return -10**9
        if not resources:
            # bias toward center if nothing to do
            return -(abs(x - (w - 1) / 2) + abs(y - (h - 1) / 2))
        best = -10**9
        for rx, ry in resources:
            sdist = cheb(x, y, rx, ry)
            odist = cheb(ox, oy, rx, ry)
            slack = odist - sdist  # higher means we can arrive sooner than opponent
            # prefer higher slack, then lower our distance; slight anti-collision bias near opponent
            val = slack * 1000 - sdist * 10 - (cheb(x, y, ox, oy))
            if val > best:
                best = val
        return best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break: fixed move order
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        val = cell_good(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]