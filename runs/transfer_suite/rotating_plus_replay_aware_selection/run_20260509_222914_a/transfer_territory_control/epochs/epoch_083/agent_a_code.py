def choose_move(observation):
    w = int(observation.get("grid_width") or 0) or 8
    h = int(observation.get("grid_height") or 0) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    cells = []
    for key in ("unclaimed_cells", "resources"):
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    cells.append((x, y))
        if cells:
            break
    if not cells:
        cells = [(ox, oy)] if 0 <= ox < w and 0 <= oy < h and (ox, oy) not in obstacles else [(sx, sy)]
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)
    cells.sort(key=lambda t: (dist(sx, sy, t[0], t[1]), t[0], t[1]))
    tx, ty = cells[0]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_t = dist(nx, ny, tx, ty)
        d_o = dist(nx, ny, ox, oy)
        score = -d_t * 10 + d_o
        if score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]