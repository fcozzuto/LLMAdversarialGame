def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        bestv = None
        for x, y in resources:
            sd = md(sx, sy, x, y)
            od = md(ox, oy, x, y)
            # Prefer resources we can reach first; otherwise deny the most (minimize opp advantage).
            v = (od - sd, -sd, x, y)  # higher first component = we are closer
            if bestv is None or v > bestv:
                bestv = v
                best = (x, y)
        tx, ty = best

    # Greedy step toward chosen target with deterministic tie-breaking; also avoid stepping into immediate opponent pressure.
    best_step = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        curd = md(nx, ny, tx, ty)
        oppd = md(nx, ny, ox, oy)
        # Prefer smaller distance to target; if tied, prefer farther from opponent (anti-deny).
        score = (-curd, oppd, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]