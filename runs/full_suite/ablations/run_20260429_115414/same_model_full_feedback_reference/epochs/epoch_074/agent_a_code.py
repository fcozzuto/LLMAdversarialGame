def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = resources[0] if resources else (ox, oy)
    if resources:
        best_r, best_d = resources[0], dist(resources[0], (sx, sy))
        for r in resources[1:]:
            d = dist(r, (sx, sy))
            if d < best_d:
                best_r, best_d = r, d
        target = best_r

    best_move = (0, 0)
    best_score = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if resources and (nx, ny) in set(resources):
            score += 10**6
        if resources:
            score += -dist((nx, ny), target) * 1000
        score += -(dist((nx, ny), (ox, oy)))  # prefer moving toward opponent if no resources/help ties
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]