def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_score = -10**18
    prefer = 0  # deterministic tie-break priority among moves

    if resources:
        for i, (dx, dy) in enumerate(moves):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            d_r = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < d_r:
                    d_r = d
            d_o = cheb(nx, ny, ox, oy)
            # Favor grabbing closer resources, but keep distance from denier.
            score = -3 * d_r + 1.2 * d_o
            # Small deterministic bias toward moving "down/right" to break symmetry.
            score += 0.01 * (dx + 0.3 * dy) + 0.0001 * i
            if score > best_score + 1e-12:
                best_score = score
                best_move = (dx, dy)
                prefer = i
    else:
        # No visible resources: go toward a corner farthest from opponent.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        target = corners[0]
        bestd = -1
        for c in corners:
            d = cheb(c[0], c[1], ox, oy)
            if d > bestd:
                bestd = d
                target = c
        tx, ty = target
        for i, (dx, dy) in enumerate(moves):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty) + 0.0001 * i
            if score > best_score + 1e-12:
                best_score = score
                best_move = (dx, dy)
                prefer = i

    return [int(best_move[0]), int(best_move[1])]