def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    pref = [(0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]

    def md2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Prefer moves that improve our advantage over opponent for some resource,
    # and secondarily reduce opponent's advantage and avoid stepping into tight regions.
    def local_penalty(nx, ny):
        # If surrounded (3+ blocked neighbors), avoid.
        cnt = 0
        for dx, dy in moves:
            tx, ty = nx + dx, ny + dy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                cnt += 1
        return 10 if cnt >= 3 else (3 if cnt == 2 else 0)

    best_score = None
    best_move = [0, 0]
    for dx, dy in pref:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_best = -10**18
        op_best = -10**18
        for rx, ry in resources:
            my_d = md2(nx, ny, rx, ry)
            op_d = md2(ox, oy, rx, ry)
            # Advantage: lower our distance and higher opponent distance.
            adv = op_d - my_d
            if adv > my_best:
                my_best = adv
            # Track where opponent can rapidly respond
            if -op_d > op_best:
                op_best = -op_d

        # Also if we're closer to any resource than opponent is, encourage.
        immediate = 0
        for rx, ry in resources:
            if md2(nx, ny, rx, ry) < md2(ox, oy, rx, ry):
                immediate = 5
                break

        score = my_best + immediate - (local_penalty(nx, ny)) + 0.1 * op_best
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]