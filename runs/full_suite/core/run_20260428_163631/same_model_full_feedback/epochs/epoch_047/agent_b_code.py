def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    if resources:
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_me = cheb(nx, ny, ox, oy)
            # Choose target that balances reaching it vs slowing opponent
            best_t = None
            best_t_val = None
            for tx, ty in resources:
                myd = cheb(nx, ny, tx, ty)
                opd = cheb(ox, oy, tx, ty)
                val = myd - 0.35 * opd
                if best_t_val is None or val < best_t_val or (val == best_t_val and (tx, ty) < best_t):
                    best_t_val = val
                    best_t = (tx, ty)
            tx, ty = best_t
            final_val = best_t_val + 0.02 * d_me  # prefer being farther from opponent on ties
            if best_val is None or final_val < best_val or (final_val == best_val and (dx, dy) < best_move):
                best_val = final_val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move to center while staying away from opponent
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        val = cheb(nx, ny, cx, cy) - 0.15 * cheb(nx, ny, ox, oy)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]