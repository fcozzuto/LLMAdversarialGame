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
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick resource that maximizes relative advantage (being closer than opponent)
    best_t = None
    best_adv = -10**9
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        adv = opd - myd  # higher => I'm closer
        # Tie-break: also prefer nearer overall
        key = adv * 100 - (myd)
        if key > best_adv:
            best_adv = key
            best_t = (rx, ry)

    if best_t is None:
        tx, ty = (w - 1, h - 1) if (sx, sy) == (0, 0) else (0, 0)
    else:
        tx, ty = best_t

    # Heuristic: move that increases my closeness to chosen target, and improves relative advantage vs opponent
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Encourage not letting opponent have the same target: if I'm not improving relative, penalize.
        rel = (opd - myd)
        # Small penalty for approaching opponent too directly (reduce collision/steal risk)
        dist_to_opp = md(nx, ny, ox, oy)
        val = rel * 1000 - myd * 10 + dist_to_opp * 1
        # If we're already at a resource, prefer staying or gentle moves keeping target
        if resources and (sx, sy) in resources:
            if (nx, ny) in resources:
                val += 10000
            else:
                val -= 200
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]