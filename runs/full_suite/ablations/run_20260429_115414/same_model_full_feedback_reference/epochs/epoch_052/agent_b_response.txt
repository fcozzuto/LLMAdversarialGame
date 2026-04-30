def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def adj_obst_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    pen += 1
        return pen

    def best_score_from(px, py):
        if not resources:
            tx, ty = W // 2, H // 2
            return -cheb(px, py, tx, ty) - 0.3 * adj_obst_pen(px, py)
        best = -10**9
        for rx, ry in resources:
            d_me = cheb(px, py, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # If opponent is closer to a resource, deprioritize it.
            score = (d_op - d_me) * 1.6 - d_me * 0.35 - adj_obst_pen(px, py) * 0.25
            # Slight preference for moving "north-west" early when tied (since starts opposite corners).
            score += (py - ry) * 0.02 + (px - rx) * 0.02
            if score > best:
                best = score
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = best_score_from(nx, ny)
        # Small tie-break to reduce oscillations: prefer chebyshev progress toward current best.
        if val > best_val or (val == best_val and cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]