def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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
    if not resources:
        tx, ty = (w - 1 if sx < w // 2 else 0), (h - 1 if sy < h // 2 else 0)
    else:
        def cheb(ax, ay, bx, by):
            dx = ax - bx
            if dx < 0: dx = -dx
            dy = ay - by
            if dy < 0: dy = -dy
            return dx if dx > dy else dy

        # Target resources where opponent is relatively farther from them.
        best = None
        for rx, ry in resources:
            dme = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # Prefer: we are closer (more negative), then closer overall, then resources farther from opponent to reduce contention.
            cand = (dme - dop, dme, -dop, rx, ry)
            if best is None or cand < best[0]:
                best = (cand, rx, ry)
        tx, ty = best[1], best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dme_next = cheb(nx, ny, tx, ty)
        dop_now = cheb(ox, oy, tx, ty)
        # Push toward target, but also avoid moves that make us easy to contest (large increase in our advantage).
        val = (dme_next, cheb(nx, ny, ox, oy), (dme_next - dop_now), - (abs(nx - tx) + abs(ny - ty)))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]