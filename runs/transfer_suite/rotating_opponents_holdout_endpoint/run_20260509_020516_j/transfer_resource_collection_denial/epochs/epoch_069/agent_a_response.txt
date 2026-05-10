def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Choose a resource we can reach strictly earlier; else the closest resource.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        # Bias toward winning the race; also keep targets not too far.
        if opd - myd >= 1:
            key = (0, myd, opd, rx + ry)
        else:
            key = (1, myd, opd, rx + ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # Obstacle-aware step: if diagonal step blocked or both coord steps blocked, try axis detours.
    candidates = []
    nx, ny = sx + dx, sy + dy
    candidates.append((dx, dy))
    if dx != 0:
        candidates.append((dx, 0))
    if dy != 0:
        candidates.append((0, dy))
    candidates.append((dx, -dy))
    candidates.append((-dx, dy))
    candidates.append((0, 0))

    def valid_step(step):
        px, py = sx + step[0], sy + step[1]
        if not (0 <= px < w and 0 <= py < h):
            return False
        if (px, py) in obstacles:
            return False
        return True

    # Prefer steps that decrease our distance to target, breaking ties deterministically.
    curd = md(sx, sy, rx, ry)
    best_step = [0, 0]
    best_score = None
    t = int(observation.get("turn_index", 0) or 0)
    for step in candidates:
        if not valid_step(step):
            continue
        nd = md(sx + step[0], sy + step[1], rx, ry)
        # Slight deterministic tie-break using turn_index parity
        score = (nd < curd, -(nd), (sx + sy + rx + ry + t) % 2, nd)
        if best_score is None or score > best_score:
            best_score = score
            best_step = [int(step[0]), int(step[1])]

    return best_step