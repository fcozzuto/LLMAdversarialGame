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
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Choose a resource where we are most ahead; if none, choose closest to the opponent (interception bias).
    best = None
    for rx, ry in resources:
        self_d = cheb((sx, sy), (rx, ry))
        opp_d = cheb((ox, oy), (rx, ry))
        advantage = opp_d - self_d  # >0 means we are closer
        # Interception: when losing, prioritize resources that are also close to opponent (strongest denial targets)
        tie = (-self_d, -opp_d) if advantage < 0 else (-(advantage), self_d)
        key = (advantage if advantage > 0 else -abs(advantage), tie)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Prefer decreasing distance to target; slight bias away from opponent when contesting
        d_self = cheb((nx, ny), (tx, ty))
        d_opp = cheb((nx, ny), (ox, oy))
        d_opptarget = cheb((ox, oy), (tx, ty))
        contest = 1 if d_opptarget <= d_self else 0
        score = (-d_self, d_opp if contest else -d_opptarget)
        if bestm is None or score > bestm[0]:
            bestm = (score, (dx, dy))

    return [bestm[1][0], bestm[1][1]]