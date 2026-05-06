def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources or not free(sx, sy):
        return [0, 0]

    rx, ry = resources[0]
    bestd = 10**18
    for p in resources:
        x, y = p
        if not inb(x, y) or (x, y) in obstacles:
            continue
        d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        if d < bestd or (d == bestd and (x, y) < (rx, ry)):
            bestd, rx, ry = d, x, y

    # Evaluate immediate move by progress to target; if equal, prefer increasing distance to opponent.
    oppx, oppy = ox, oy
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_t = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
        d_o = (oppx - nx) * (oppx - nx) + (oppy - ny) * (oppy - ny)
        # Higher score is better: maximize reduction to target, then maximize separation from opponent.
        score = -d_t + (d_o // 10)
        if score > best_score:
            best_score, best_move = score, (dx, dy)
        elif score == best_score and (dx, dy) < best_move:
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]