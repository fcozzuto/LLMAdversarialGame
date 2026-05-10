def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not moves:
        return [0, 0]

    resources = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]
    unclaimed = [(int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or [])]

    unclaimed_set = set(unclaimed)
    res_set = set(resources)

    targets = []
    if resources:
        targets = resources
    elif unclaimed:
        targets = unclaimed
    else:
        targets = [(w // 2, h // 2), (ox, oy)]

    tx, ty = targets[0]
    bestd = None
    for x, y in targets:
        d = abs(x - sx) + abs(y - sy)
        if bestd is None or d < bestd or (d == bestd and (x, y) < (tx, ty)):
            bestd, tx, ty = d, x, y

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0
        if (nx, ny) in res_set:
            score += 10000
        elif (nx, ny) in unclaimed_set:
            score += 5000
        score += -((abs(tx - nx) + abs(ty - ny)))
        score += -0.1 * (abs(ox - nx) + abs(oy - ny))
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]