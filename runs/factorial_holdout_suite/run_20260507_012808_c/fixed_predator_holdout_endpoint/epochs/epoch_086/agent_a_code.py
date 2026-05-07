def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
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

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = resources[0]
    best_margin = md(ox, oy, best[0], best[1]) - md(sx, sy, best[0], best[1])
    for tx, ty in resources[1:]:
        margin = md(ox, oy, tx, ty) - md(sx, sy, tx, ty)
        if margin > best_margin:
            best_margin = margin
            best = (tx, ty)
        elif margin == best_margin:
            if md(sx, sy, tx, ty) < md(sx, sy, best[0], best[1]):
                best = (tx, ty)

    tx, ty = best
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd = md(nx, ny, tx, ty)
        od = md(ox, oy, tx, ty)
        score = sd - od  # lower is better; keeps winning targets closer
        if score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]