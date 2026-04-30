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
        return [0, 0]

    try:
        rem = int(observation.get("remaining_resource_count"))
    except:
        rem = len(resources)
    late = rem <= 4

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def risk(x, y):
        r = 0
        for bx, by in obstacles:
            if cheb(x, y, bx, by) <= 1:
                r += 1
        return r

    best = None
    bestv = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we arrive earlier (or opponent is far),
        # avoid obstacle-adjacent cells, and tighten focus near the end.
        v = (ds - 0.95 * do)
        v += 0.35 * risk(rx, ry)
        if late:
            v += 0.15 * ds
        else:
            v += 0.05 * ds
        if bestv is None or v < bestv:
            bestv = v
            best = (rx, ry)

    tx, ty = best

    steps = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dcur = cheb(nx, ny, tx, ty)
        # Also avoid stepping into risky areas when possible.
        score = dcur * 10 + risk(nx, ny)
        # Deterministic tie-break: lexicographic (dx, dy) preference via order in steps.
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]