def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Estimate "control": choose resources where we are relatively closer than opponent.
    best = None
    best_key = None
    for tx, ty in resources:
        myd = man(sx, sy, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Prefer: we close the advantage (myd - opd small), then our closeness, then deterministic tie-break.
        key = (myd - opd, myd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # One-step greedy toward chosen target; if blocked, keep best feasible.
    best_move = (0, 0)
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = man(nx, ny, tx, ty)
        # Tie-break also discourages moves that reduce our lead being negative (if applicable).
        opd2 = man(ox, oy, tx, ty)
        eval_key = (myd2 - opd2, myd2, dx, dy)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]