def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def clamp_pos(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for a in observation.get("obstacles") or []:
        x = y = None
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        if x is not None and y is not None and clamp_pos(x, y):
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x = y = None
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        if x is not None and y is not None and clamp_pos(x, y) and (x, y) not in obstacles:
            resources.append((x, y))

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = cd(sx, sy, rx, ry)
            od = cd(ox, oy, rx, ry)
            gain = od - sd
            key = (-gain, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
        if sx == tx and sy == ty:
            return [0, 0]
        best_move = [0, 0]
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not clamp_pos(nx, ny) or (nx, ny) in obstacles:
                continue
            score = (cd(nx, ny, tx, ty), cd(ox, oy, tx, ty) - cd(nx, ny, tx, ty), dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    # No resources: head toward opponent (minimize distance), avoid obstacles.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_pos(nx, ny) or (nx, ny) in obstacles:
            continue
        score = (cd(nx, ny, ox, oy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move