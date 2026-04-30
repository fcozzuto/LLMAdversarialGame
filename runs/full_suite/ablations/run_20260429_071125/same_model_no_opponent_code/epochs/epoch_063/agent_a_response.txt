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
    any_toward = None

    # Strategy shift vs previous epoch: mostly greedy for nearest; if opponent is much closer, switch to a resource that "punishes" their advantage.
    best = None  # (key, target)
    for r in resources:
        myd = cd(my, r)
        opd = cd(opp, r)
        # If we're not close and opponent is clearly nearer, prefer resources where opponent advantage shrinks (or reverses).
        if opd - myd >= 2:
            key = (0, myd, -(opd - myd), r[0], r[1])  # smaller myd, reduce opponent advantage
        else:
            key = (1, myd, (opd - myd), r[0], r[1])   # greedy to nearest; tie-break deterministically
        if best is None or key < best[0]:
            best = (key, r)

    target = best[1]

    dirs = (-1, 0, 1)
    moves = [(dx, dy) for dx in dirs for dy in dirs if not (dx == 0 and dy == 0)] + [(0, 0)]
    best_move = (10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd2 = cd((nx, ny), target)
        opd2 = cd((nx, ny), opp)
        # Prefer decreasing distance to target; when tied, keep away from opponent if possible.
        key = (myd2, -opd2, abs(nx - sx) + abs(ny - sy), nx, ny)
        if key < best_move[0:1] or best_move[1] is None:
            best_move = (key[0:1][0], (dx, dy))
    if best_move[1] is None:
        # Fallback: deterministic local valid step toward target.
        tx, ty = target
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        for ddx in (0, -1 if tx < sx else 1 if tx > sx else 0):
            for ddy in (0, -1 if ty < sy else 1 if ty > sy else 0):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = sx + ddx, sy + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [ddx, ddy]
        return [0, 0]
    return [int(best_move[1][0]), int(best_move[1][1])]