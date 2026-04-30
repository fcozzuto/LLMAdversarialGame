def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Deterministic tie-breakers: prefer diagonal->orthogonal->stay order already fixed by dirs,
    # then prefer closer-to-center move, then lexicographic.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = [0, 0]
    best_score = -10**30

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = -d2(nx, ny, ox, oy)  # keep distance
            score += -0.01 * d2(nx, ny, cx, cy)  # also drift to center a bit
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # Race heuristic: for each move, compute best resource advantage.
    # Advantage = -own_dist + 0.85*op_dist to that same resource, and small bias to reachable first.
    # Also slightly avoid stepping away from any resource cluster by using min own_dist over top resources.
    top = resources[:]
    # Sort deterministically by position to avoid dependence on list order
    top.sort()
    top = top[:12]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        own_min = 10**18
        best_adv = -10**18
        for rx, ry in top:
            od = d2(nx, ny, rx, ry)
            opd = d2(ox, oy, rx, ry)
            if od < own_min:
                own_min = od
            adv = -od + 0.85 * opd
            if adv > best_adv:
                best_adv = adv
        center_bias = -0.01 * d2(nx, ny, cx, cy)
        score = best_adv - 0.001 * own_min + center_bias
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move