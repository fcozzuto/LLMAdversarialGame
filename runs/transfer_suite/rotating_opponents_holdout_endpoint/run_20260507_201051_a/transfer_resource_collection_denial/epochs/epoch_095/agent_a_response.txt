def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda d: (d[0] == 0 and d[1] == 0, d[0], d[1]))

    if not resources:
        tx, ty = w // 2, h // 2
        return [0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1)]

    def steps(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        pos = (nx, ny)
        penalty = -10**9 if pos in obstacles else 0

        my_best = 10**9
        opp_best = -10**9
        for rx, ry in resources:
            my_d = steps(nx, ny, rx, ry)
            opp_d = steps(ox, oy, rx, ry)
            if my_d < my_best:
                my_best = my_d
            if opp_d > opp_best:
                opp_best = opp_d

        # primary: maximize lead toward a resource (opp_d - my_d), secondary: minimize my_best
        lead = opp_best - my_best
        score = (penalty + lead, -my_best)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move