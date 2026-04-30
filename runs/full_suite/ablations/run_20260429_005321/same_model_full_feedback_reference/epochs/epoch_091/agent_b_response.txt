def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_score(nx, ny):
        if not resources:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dcent = abs(nx - cx) + abs(ny - cy)
            dop = cheb(nx, ny, ox, oy)
            return -dcent * 0.02 + dop * 0.001
        # Target contested resources first: maximize (dist_op - dist_us), then closeness to ours.
        best = -10**9
        for rx, ry in resources:
            dus = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # If we can reach much sooner than opponent, prioritize heavily.
            rel = dop - dus
            score = rel * 3.0 - dus * 0.6
            if score > best:
                best = score
        # Also slightly prefer being farther from opponent to reduce interference.
        return best + cheb(nx, ny, ox, oy) * 0.03

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-breaking: lexicographic on (dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = move_score(nx, ny)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]