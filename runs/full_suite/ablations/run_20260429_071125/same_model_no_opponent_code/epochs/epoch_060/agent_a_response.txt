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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources, maximize separation from opponent.
    if not resources:
        best = (-(10**9), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = dist((nx, ny), (ox, oy))
            if v > best[0]:
                best = (v, dx, dy)
        return [int(best[1]), int(best[2])]

    # Select a target resource where we have the best advantage.
    best = None
    for r in resources:
        myd = dist((sx, sy), r)
        opd = dist((ox, oy), r)
        adv = opd - myd  # larger means opponent is effectively farther
        # Tie-breakers: prefer closer and then deterministic coordinate preference
        key = (adv, -myd, -(r[0] * 10 + r[1]))
        if best is None or key > best[0]:
            best = (key, r)
    target = best[1]

    # Move one step to reduce distance to the chosen target while keeping move valid.
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dist((nx, ny), target)
        # secondary: keep/extend lead in case opponent can contest
        oppd_after = dist((ox, oy), target)
        lead = oppd_after - nd
        # tertiary: avoid moving toward opponent too much
        sep = dist((nx, ny), (ox, oy))
        score = (lead, -nd, sep, -(dx * dx + dy * dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        # Should be rare; fallback to staying still if blocked everywhere.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]