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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If no resources, head to center of their side (deterministic drift) while staying safe.
    if not resources:
        tx, ty = w - 1, h // 2
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -d2(nx, ny, tx, ty) - (1 if (nx, ny) == (ox, oy) else 0)
            if v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    best = (-10**18, 0, 0)
    # Strategy: for each move, compute "contest value" for resources:
    # prefer resources where we can beat opponent (mydist < opdists), else block closer ones.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # immediate value (0..)
        score = -d2(nx, ny, sx, sy) * 0.01
        if (nx, ny) in resources:
            score += 10**6  # deterministic grab if stepping onto a resource

        # Evaluate all resources; keep it cheap: use best 2 categories.
        win_best = -10**18
        contest_best = -10**18
        for rx, ry in resources:
            myd = d2(nx, ny, rx, ry)
            opd = d2(ox, oy, rx, ry)
            diff = opd - myd  # positive means we are closer
            # winning: myd smaller
            if myd < opd:
                v = diff * 2.0 - myd * 0.001
                if v > win_best:
                    win_best = v
            else:
                # contest/block: reduce opponent lead; also avoid resources too far from us
                v = diff * 1.0 - myd * 0.0005
                if v > contest_best:
                    contest_best = v
        score += max(win_best, contest_best) * 10.0

        # Anti-stall: mildly prefer moves that also increase distance from opponent's exact position
        score += (d2(nx, ny, ox, oy) - d2(sx, sy, ox, oy)) * 0.001

        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [best[1], best[2]]