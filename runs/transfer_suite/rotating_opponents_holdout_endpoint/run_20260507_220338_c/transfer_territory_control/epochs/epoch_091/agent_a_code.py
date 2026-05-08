def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obstacles.add((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = (10**9, 0)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        penalty = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            bx, by = nx + ax, ny + ay
            if inside(bx, by) and (bx, by) in obstacles:
                penalty += 1
        score = (d, penalty, 0 if (dx, dy) == (0, 0) else -1)
        if score < best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]