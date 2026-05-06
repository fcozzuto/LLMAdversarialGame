def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def best_value(px, py):
        if resources:
            best = None
            for r in resources:
                rx, ry = r
                if (rx, ry) in obstacles:
                    continue
                da = cheb((px, py), (rx, ry))
                do = cheb((ox, oy), (rx, ry))
                # Prefer resources we can get sooner, and where opponent is comparatively far.
                val = (do - da, -da, rx, ry)
                if best is None or val > best[0]:
                    best = (val, (rx, ry))
            if best is not None:
                return best[0], best[1]
            # If all resources blocked, fall through to heading opponent.
        # No (available) resources: try to reduce distance to opponent to deny.
        dself = cheb((px, py), (ox, oy))
        val = (-dself, 0, 0, 0)
        return val, (ox, oy)

    if not inb(sx, sy):
        return [0, 0]

    best_move = [0, 0]
    best_score = None
    best_target = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val, target = best_value(nx, ny)

        # Small tie-break: also prefer moves that keep approaching the current preferred target.
        if resources and target is not None:
            tx, ty = target
            approach = -cheb((nx, ny), (tx, ty))
        else:
            approach = 0

        score = (val[0], val[1], val[2], val[3], approach, -cheb((nx, ny), (ox, oy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
            best_target = target

    if best_score is None:
        return [0, 0]
    return best_move