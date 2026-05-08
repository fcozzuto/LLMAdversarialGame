def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)

    target = None
    if unclaimed:
        best = None
        bestd = None
        for (x, y) in unclaimed:
            if not inside(x, y) or (x, y) in obstacles:
                continue
            d = dist(sx, sy, x, y)
            if bestd is None or d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        target = best

    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is not None:
            score = -dist(nx, ny, target[0], target[1])
        else:
            score = dist(nx, ny, ox, oy)
        moves.append((score, dx, dy))
    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [moves[0][1], moves[0][2]]