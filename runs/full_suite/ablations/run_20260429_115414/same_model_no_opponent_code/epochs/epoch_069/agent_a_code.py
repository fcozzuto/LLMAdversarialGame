def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cd(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = ox, oy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        for mx, my in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [mx, my]
        return [0, 0]

    best = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        # Prefer resources I'm closer to; if not, prefer those opponent is far from.
        key = (myd - opd, myd, (rx + ry) % 2, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    best_move = (10**9, 10**9, 10**9, 0, 0)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cd(nx, ny, tx, ty)
        opd2 = cd(ox, oy, tx, ty)
        # Extra nudge: if we can step onto a resource, prioritize hard.
        on_res = 1 if (nx, ny) in set(resources) else 0
        # Keep moves deterministic in tie by fixed ordering of moves.
        score = (-on_res, myd2, myd2 - opd2, (nx + ny) % 2, nx, ny)
        if score < best_move[:len(score)]:
            best_move = (score[0], score[1], score[2], mx, my)
    return [int(best_move[3]), int(best_move[4])]