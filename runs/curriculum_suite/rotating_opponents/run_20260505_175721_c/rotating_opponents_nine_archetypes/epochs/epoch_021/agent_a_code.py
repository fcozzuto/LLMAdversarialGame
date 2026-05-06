def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        def cheb(x1, y1, x2, y2):
            dx = x1 - x2
            if dx < 0: dx = -dx
            dy = y1 - y2
            if dy < 0: dy = -dy
            return dx if dx >= dy else dy

        # Prefer resources we can reach earlier; otherwise contest the closest-to-opponent ones.
        best = None
        for rx, ry in resources:
            st = cheb(sx, sy, rx, ry)
            ot = cheb(ox, oy, rx, ry)
            advantage = ot - st  # positive means we arrive first
            # primary: maximize advantage; secondary: minimize our time to reduce overcommit
            key = (-advantage, st, rx, ry)  # deterministic tie-break
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    if sx == tx and sy == ty:
        return [0, 0]

    def target_after(nx, ny):
        dx = tx - nx
        if dx > 0: dx = 1
        elif dx < 0: dx = -1
        dy = ty - ny
        if dy > 0: dy = 1
        elif dy < 0: dy = -1
        return dx, dy

    # Choose the valid move that most reduces chebyshev distance to target (tie-break by step ordering).
    def cheb_dist(nx, ny):
        dx = tx - nx
        if dx < 0: dx = -dx
        dy = ty - ny
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best_move = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = cheb_dist(nx, ny)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]