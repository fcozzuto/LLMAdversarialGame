def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list if isinstance(p, (list, tuple)) and len(p) >= 2)

    resources_list = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources_list:
        best_move = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = None
            for r in resources_list:
                if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                    continue
                rx, ry = r
                if not inb(rx, ry) or (rx, ry) in obstacles:
                    continue
                ss = d2(nx, ny, rx, ry)
                os = d2(ox, oy, rx, ry)
                v = ss - 1.5 * os
                if score is None or v < score or (v == score and (rx, ry) < best_target):
                    score = v
                    best_target = (rx, ry)
            if score is None:
                continue
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = w // 2, h // 2
    best_move = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = d2(nx, ny, tx, ty)
        if bestv is None or v < bestv or (v == bestv and (dx, dy) < best_move):
            bestv = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]