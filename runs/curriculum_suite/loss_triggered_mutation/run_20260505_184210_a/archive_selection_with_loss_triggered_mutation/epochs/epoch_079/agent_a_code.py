def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def step_score(px, py):
        if not resources:
            tx, ty = w // 2, h // 2
            return -man((px, py), (tx, ty))
        best = -10**9
        best2 = 10**9
        for r in resources:
            myd = man((px, py), r)
            opd = man((ox, oy), r)
            diff = opd - myd  # positive means I'm closer (denial / grab)
            if diff > best or (diff == best and myd < best2):
                best, best2 = diff, myd
        return best * 1000 - best2

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = step_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
        elif v == best_val:
            # deterministic tie-break: prefer smaller dx magnitude then smaller dy magnitude then stay
            if abs(dx) < abs(best_move[0]) or (abs(dx) == abs(best_move[0]) and (abs(dy) < abs(best_move[1]) or (abs(dy) == abs(best_move[1]) and dx == best_move[0] and dy == best_move[1]))):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]