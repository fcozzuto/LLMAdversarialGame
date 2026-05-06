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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def best_target():
        if resources:
            best = None
            for rx, ry in resources:
                ds = cheb(sx, sy, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources where we are at least as close as opponent; otherwise take those where opponent is most over-advantaged.
                primary = (do - ds) if ds <= do else -ds
                # Tie-break toward closer resources for faster collection.
                tie = ds + 0.01 * (rx + ry)
                cand = (primary, -tie, rx, ry)
                if best is None or cand > best:
                    best = cand
            return best[2], best[3]
        return (w - 1) // 2, (h - 1) // 2

    tx, ty = best_target()

    # If target cell is blocked, fall back to nearest valid move toward open center
    if (tx, ty) in obstacles:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_mv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_target = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Move to reduce target distance; also keep some distance from opponent to avoid giving them first pick.
        score = (-d_target) + 0.08 * d_opp
        if best_mv is None or score > best_mv[0]:
            best_mv = (score, dx, dy)

    if best_mv is None:
        return [0, 0]
    return [int(best_mv[1]), int(best_mv[2])]