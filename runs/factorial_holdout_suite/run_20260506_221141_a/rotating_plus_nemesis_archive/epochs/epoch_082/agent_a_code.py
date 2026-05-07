def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        tx, ty = resources[0]
        best = man(sx, sy, tx, ty)
        for (x, y) in resources[1:]:
            d = man(sx, sy, x, y)
            if d < best or (d == best and (y, x) < (ty, tx)):
                best, tx, ty = d, x, y

        best_move = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            s = -man(nx, ny, tx, ty)
            s += 0.01 * man(nx, ny, ox, oy)
            if best_score is None or s > best_score or (s == best_score and (dx, dy) < best_move):
                best_score, best_move = s, (dx, dy)
        if best_score is not None:
            return [int(best_move[0]), int(best_move[1])]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = man(nx, ny, ox, oy)
        if best_score is None or s > best_score or (s == best_score and (dx, dy) < best_move):
            best_score, best_move = s, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]