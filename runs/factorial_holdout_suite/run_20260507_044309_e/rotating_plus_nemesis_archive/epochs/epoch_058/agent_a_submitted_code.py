def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def dist_m(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = min(resources, key=lambda p: (dist_m((sx, sy), p), p[0], p[1]))
    best = (10**9, 10**9, 10**9, 0, 0)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist_m((nx, ny), target)
        score_penalty = 0 if (nx, ny) == (ox, oy) else 1
        # Prefer moves that get closer; lightly avoid stepping onto opponent.
        key = (d, -dx * 0, -dy * 0, -score_penalty, dx, dy)
        if key < (best[0], best[1], best[2], best[3], best[4], best[5]):
            best = (d, dx, dy, -score_penalty, dx, dy)

    return [best[4], best[5]]