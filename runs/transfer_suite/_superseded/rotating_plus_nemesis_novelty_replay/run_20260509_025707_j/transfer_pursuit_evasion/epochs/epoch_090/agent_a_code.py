def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                targets.append((x, y))

    if targets:
        best = None
        bestd = None
        for x, y in targets:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if bestd is None or d < bestd or (d == bestd and (x, y) > best):
                bestd = d
                best = (x, y)
        tx, ty = best
        best_move = (0, 0)
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d2 = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            score = (d2, -abs(nx - ox) - abs(ny - oy), -nx, -ny)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources known: flee from opponent deterministically.
    best_move = (0, 0)
    bestd = -1
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if d > bestd or (d == bestd and (nx, ny) > (sx + best_move[0], sy + best_move[1])):
            bestd = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]