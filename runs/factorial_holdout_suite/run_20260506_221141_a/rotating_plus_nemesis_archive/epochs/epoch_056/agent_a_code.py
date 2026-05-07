def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_pos = (nx, ny)
        my_score = 0
        # Prefer moves that make us closer to valuable nearby resources than opponent.
        for res in resources:
            dm = dist(my_pos, res)
            do = dist((ox, oy), res)
            # Strongly prioritize resources we can reach sooner; hedge with "close enough" term.
            if dm < do:
                my_score += 40 - 10 * dm
            elif dm == do:
                my_score += 12 - 4 * dm
            else:
                my_score -= 8 + 2 * (dm - do)

        # Mild additional bias to avoid dead-ends near obstacles: discourage stepping adjacent to many obstacles.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    adj += 1
        my_score -= 2 * adj

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying still.
        if my_score > best_val or (my_score == best_val and (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1])):
            best_val = my_score
            best_move = [dx, dy]

    return best_move