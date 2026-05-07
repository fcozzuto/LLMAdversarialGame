def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    tx, ty = min(resources, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dcur = md(nx, ny, tx, ty)
        dopp = md(nx, ny, ox, oy)
        score = -dcur * 10 - dopp
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    if best_score == -10**18:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]