def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role)  # pursuer => minimize distance; else maximize

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = x - ox
        if dx < 0: dx = -dx
        dy = y - oy
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_move(x, y):
        d = cheb(x, y)
        # Prefer staying away from borders and obstacles to avoid getting pinned near walls.
        edge = min(x, y, w - 1 - x, h - 1 - y)
        edge_bias = edge / float(max(1, min(w, h) - 1))
        # Slight preference for moving along the best direction (diagonal if possible).
        diag_align = 0
        if (x - sx) != 0 and (y - sy) != 0:
            diag_align = 0.02
        # If moving closer/farther along Chebyshev helps, reward it.
        prev_d = cheb(sx, sy)
        delta = d - prev_d
        # For pursuer: want smaller d => negative delta is good. For evader: positive delta is good.
        prog = (-delta if is_pursuer else delta) * 0.2
        # Combine: main term is distance; then biases.
        main = -d if is_pursuer else d
        return main + 0.8 * edge_bias + diag_align + prog

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**9 if is_pursuer else -10**9
        else:
            val = score_move(nx, ny)
        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if is_pursuer:
                if val > best_val + 1e-12:
                    best_val = val
                    best_move = [dx, dy]
            else:
                if val > best_val + 1e-12:
                    best_val = val
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]