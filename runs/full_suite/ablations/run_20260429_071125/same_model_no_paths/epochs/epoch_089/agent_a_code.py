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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target():
        if not resources:
            return (ox, oy)
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gap = do - ds  # positive => we closer
            # Material shift: actively pursue resources we are closer for; otherwise pick the one that maximizes
            # "survivability" by reducing the opponent advantage as much as possible.
            if gap >= 0:
                sc = 100 * gap - ds  # strong preference
            else:
                sc = 2 * gap - 0.5 * ds + 0.1 * do  # avoid hopeless races, but still reduce damage
            # Mild tie-breaker: bias away from opponent by prefering targets where we're "less behind"
            sc += 0.02 * (ds - do)
            if best is None or sc > best[0] or (sc == best[0] and (rx, ry) < (best[2], best[3])):
                best = (sc, ds, rx, ry)
        return (best[2], best[3])

    tx, ty = best_target()

    # Move choice: minimize distance to target, but also add a deterministic "pressure" term
    # to avoid moving into the opponent's nearest neighborhood.
    options = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer staying away from opponent unless it also improves target distance
        val = d_to + 0.15 * (7 - d_opp if d_opp < 7 else 0)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]