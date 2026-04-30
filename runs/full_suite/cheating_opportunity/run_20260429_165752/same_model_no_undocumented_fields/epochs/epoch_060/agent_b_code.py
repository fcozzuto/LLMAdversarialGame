def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    if not free(sx, sy):
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if resources:
        def dist(a, b, c, d):
            dx = a - c
            if dx < 0:
                dx = -dx
            dy = b - d
            if dy < 0:
                dy = -dy
            return dx + dy

        best_move = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            ns = dist(nx, ny, ox, oy)
            best_res = 10**9
            for rx, ry in resources:
                best_res = min(best_res, dist(nx, ny, rx, ry))
            score = best_res * 1000 - ns
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        if best_move is not None:
            return [best_move[0], best_move[1]]

    # Fallback: deterministic move that maximizes distance from opponent while staying legal
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        score = d
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]
    return [0, 0]