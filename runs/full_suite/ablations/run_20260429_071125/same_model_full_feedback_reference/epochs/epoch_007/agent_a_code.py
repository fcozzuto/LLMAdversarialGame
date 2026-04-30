def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def pick_target():
        if resources:
            best = None
            for rx, ry in resources:
                d = dist(sx, sy, rx, ry)
                if best is None or d < best[0]:
                    best = (d, rx, ry)
            return best[1], best[2]
        return w // 2, h // 2

    tx, ty = pick_target()

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = dist(nx, ny, tx, ty)
        opp = dist(nx, ny, ox, oy)
        score = score * 1000 + (0 if resources else -opp)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if inb(sx + best_move[0], sy + best_move[1]) else [0, 0]