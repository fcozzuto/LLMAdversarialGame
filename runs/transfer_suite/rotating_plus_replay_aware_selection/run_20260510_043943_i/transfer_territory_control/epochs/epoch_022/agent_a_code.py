def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    cells = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                cells.append((x, y))
    if cells:
        cells.sort(key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        cells = cells[:25]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        if cells:
            s = 0
            for tx, ty in cells:
                ds = dist(nx, ny, tx, ty)
                do = dist(ox, oy, tx, ty)
                s += (do - ds) - 0.01 * ds
            score = s
        else:
            score = -dist(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]