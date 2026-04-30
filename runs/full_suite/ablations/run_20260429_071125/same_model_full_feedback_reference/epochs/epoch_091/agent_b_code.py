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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Go toward opponent corner only if safe, otherwise drift away from obstacles
        best = (0, 0)
        best_s = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                s = -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
                if s > best_s:
                    best_s, best = s, (dx, dy)
        return [best[0], best[1]]

    # Pick nearest (ties deterministically by position)
    nearest = None
    best_rd = 10**18
    for r in resources:
        d = abs(sx - r[0]) + abs(sy - r[1])
        if d < best_rd or (d == best_rd and (r[0], r[1]) < (nearest[0], nearest[1])):
            best_rd = d
            nearest = r

    tx, ty = nearest
    # Heuristic scoring: minimize distance to target, maximize distance from opponent, avoid stepping near obstacles
    def score(nx, ny):
        dtn = abs(nx - tx) + abs(ny - ty)
        dtop = abs(nx - ox) + abs(ny - oy)
        # obstacle proximity penalty
        prox = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (nx + ex, ny + ey) in obstacles:
                    prox += 1
        # If we're close to opponent, prefer to not give them an easy contest (increase separation)
        contest = 0
        if dtop <= 2:
            contest = (3 - dtop) * 6
        # Encourage movement direction (reduce wasted steps)
        dir_bonus = 0
        if (tx - sx) != 0 or (ty - sy) != 0:
            dir_bonus = 1 if ((nx - sx) == (1 if tx > sx else -1 if tx < sx else 0) or (tx == sx)) else 0
            dir_bonus += 1 if ((ny - sy) == (1 if ty > sy else -1 if ty < sy else 0) or (ty == sy)) else 0
        return (-dtn * 20) + (dtop * 3) - prox * 5 - contest + dir_bonus

    best_move = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            sc = score(nx, ny)
            if sc > best_sc or (sc == best_sc and (dx, dy) < best_move):
                best_sc, best_move = sc, (dx, dy)

    return [best_move[0], best_move[1]]