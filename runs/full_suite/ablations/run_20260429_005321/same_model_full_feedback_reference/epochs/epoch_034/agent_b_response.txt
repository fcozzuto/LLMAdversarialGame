def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            move_best = -10**18
            for rx, ry in resources:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                if md == 0:
                    score = 10**6
                else:
                    score = (od - md) * 1000 - md * 3 + (abs(rx - ox) + abs(ry - oy)) * 0.01
                if score > move_best:
                    move_best = score
            # Tie-break: prefer decreasing distance to opponent (deterministic, small)
            tie = -cheb(nx, ny, ox, oy) * 0.001
            total = move_best + tie
            if total > best_score:
                best_score = total
                best_move = (dx, dy)
    else:
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            total = cheb(nx, ny, ox, oy) * 10 - (abs(nx - 0) + abs(ny - 0)) * 0.001
            if total > best_score:
                best_score = total
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]