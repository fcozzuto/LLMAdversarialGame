def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    best = None
    best_score = None
    any_legal = False

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            any_legal = True
            if resources:
                dist_res = 10**9
                for rx, ry in resources:
                    d = man(nx, ny, rx, ry)
                    if d < dist_res:
                        dist_res = d
                score = -dist_res * 10 + man(nx, ny, ox, oy)
            else:
                score = -man(nx, ny, 0, 0) - man(nx, ny, w - 1, h - 1) + man(nx, ny, ox, oy)
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]

    if best is not None:
        return best
    return [0, 0] if not any_legal else [0, 0]