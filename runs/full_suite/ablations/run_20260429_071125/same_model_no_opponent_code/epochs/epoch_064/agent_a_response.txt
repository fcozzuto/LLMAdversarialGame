def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cd(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    my = (sx, sy)
    opp = (ox, oy)
    scored = []
    for r in resources:
        myd = cd(my, r)
        opd = cd(opp, r)
        # Prefer resources where opponent is not significantly closer; otherwise still take good "swing" targets.
        swing = opd - myd
        key = (swing * 4 - myd, -opd, r[0], r[1])
        scored.append((key, r))
    scored.sort(reverse=True)
    target = scored[0][1]

    best_move = [0, 0]
    best_dist = 10**9
    # If multiple, pick deterministic tie-break toward decreasing x then y toward target.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((nx, ny, dx, dy))
    # Include staying still if all moves blocked or if it is equally good.
    candidates.append((sx, sy, 0, 0))

    for nx, ny, dx, dy in candidates:
        d = cd((nx, ny), target)
        if d < best_dist:
            best_dist = d
            best_move = [dx, dy]
        elif d == best_dist:
            # tie-break: prefer moves that reduce opponent's distance to target less (i.e., don't help them), then deterministic coordinate order
            myd = cd((nx, ny), target)
            opd = cd(opp, target)
            # slight preference for moves that move in direction of target
            tx_dir = 0
            if target[0] > nx:
                tx_dir = 1
            elif target[0] < nx:
                tx_dir = -1
            ty_dir = 0
            if target[1] > ny:
                ty_dir = 1
            elif target[1] < ny:
                ty_dir = -1
            tie = (0 if (tx_dir == 0 or dx == tx_dir) else 1,
                    0 if (ty_dir == 0 or dy == ty_dir) else 1,
                    -opd, dx, dy)
            cur = (0 if (tx_dir == 0 or best_move[0] == tx_dir) else 1,
                   0 if (ty_dir == 0 or best_move[1] == ty_dir) else 1,
                   -opd, best_move[0], best_move[1])
            if tie < cur:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]