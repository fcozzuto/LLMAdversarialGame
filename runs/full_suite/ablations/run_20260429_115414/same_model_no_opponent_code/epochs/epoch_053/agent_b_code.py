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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    prefs = {(0, -1): 0, (-1, 0): 1, (0, 0): 2, (0, 1): 3, (1, 0): 4, (-1, -1): 5, (-1, 1): 6, (1, -1): 7, (1, 1): 8}

    tx, ty = ox, oy
    if resources:
        best = None
        bestd = None
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if bestd is None or d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        tx, ty = best

    curd = abs(tx - sx) + abs(ty - sy)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        score = (curd - nd) * 1000 - nd
        score += -abs(ox - nx) - abs(oy - ny) * 0.001
        score += -prefs.get((dx, dy), 99) * 0.0001
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]