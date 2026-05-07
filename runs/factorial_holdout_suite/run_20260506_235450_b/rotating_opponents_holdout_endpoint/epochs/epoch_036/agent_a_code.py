def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        return abs(ax - bx) if abs(ax - bx) > abs(ay - by) else abs(ay - by)

    best = None
    best_score = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Favor resources we are closer to; penalize those opponent can reach sooner.
        score = (myd - 1.25 * opd) + 0.02 * cheb(sx, sy, ox, oy)
        # Slight preference to avoid long detours early: favor smaller myd when tied.
        if best is None or score < best_score - 1e-9 or (abs(score - best_score) <= 1e-9 and myd < cheb(sx, sy, best[0], best[1])):
            best = (rx, ry)
            best_score = score

    tx, ty = best

    deltas = [
        [0, 0], [1, 0], [-1, 0], [0, 1], [0, -1],
        [1, 1], [1, -1], [-1, 1], [-1, -1]
    ]
    best_move = [0, 0]
    best_cost = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        cost = (myd2 - 1.25 * opd2) + 0.02 * cheb(nx, ny, ox, oy)
        if best_cost is None or cost < best_cost - 1e-9:
            best_cost = cost
            best_move = [dx, dy]

    return best_move