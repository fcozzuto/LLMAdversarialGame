def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        targets = resources
    else:
        targets = [(w // 2, h // 2)]

    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        pos = (nx, ny)

        cur_best = -10**18
        for r in targets:
            own = dist(pos, r)
            opp = dist((ox, oy), r)
            s = (opp - own) * 10 - own
            if s > cur_best:
                cur_best = s

        # tie-break deterministically toward smaller own distance to nearest target
        if best_score is None or cur_best > best_score:
            best_score = cur_best
            best_move = [dx, dy]
        elif cur_best == best_score:
            cur_best_own = min(dist((nx, ny), r) for r in targets)
            best_own = min(dist((sx + best_move[0], sy + best_move[1]), r) for r in targets)
            if cur_best_own < best_own:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]