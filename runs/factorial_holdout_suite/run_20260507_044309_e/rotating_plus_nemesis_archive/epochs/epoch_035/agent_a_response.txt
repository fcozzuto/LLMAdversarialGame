def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles") or []:
        try:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))
        except:
            pass

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]
    if not resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            v = (abs(nx - ox) + abs(ny - oy), abs(nx - sx) + abs(ny - sy))
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_best_d = None
    for rx, ry in resources:
        d = dist(ox, oy, rx, ry)
        if opp_best_d is None or d < opp_best_d:
            opp_best_d = d

    best_next = None
    best_score = None
    for dx, dy, nx, ny in moves:
        score = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            margin = od - sd
            # If we can beat opponent, prioritize; otherwise avoid "far" from opponent's nearest.
            front = 1 if sd <= od else 0
            opp_prox_pen = max(0, od - opp_best_d)  # smaller is better
            cell_score = (front, margin, -opp_prox_pen, -sd, -dist(nx, ny, rx, ry))
            if score is None or cell_score > score:
                score = cell_score
        if best_score is None or score > best_score:
            best_score = score
            best_next = (dx, dy)

    return [int(best_next[0]), int(best_next[1])]