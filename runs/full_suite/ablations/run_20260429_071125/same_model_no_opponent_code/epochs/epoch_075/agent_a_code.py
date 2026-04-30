def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    # Find nearest resource once (deterministic)
    target = None
    if resources:
        mind = None
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if mind is None or d < mind or (d == mind and (x, y) < target):
                mind = d
                target = (x, y)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if target is None:
            # If no resources known, move to increase distance from opponent
            dist_op = cheb(nx, ny, ox, oy)
            score = dist_op
        else:
            dist_res = cheb(nx, ny, target[0], target[1])
            dist_op = cheb(nx, ny, ox, oy)
            # Prefer reducing resource distance, and avoid approaching opponent slightly
            score = (-dist_res * 1000) + (dist_op * 5)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # Deterministic tie-break: smallest dx, then dy
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]