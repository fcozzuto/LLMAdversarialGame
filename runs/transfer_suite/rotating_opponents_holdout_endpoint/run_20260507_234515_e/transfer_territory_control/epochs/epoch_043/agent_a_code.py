def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def collect(key):
        out = []
        for p in observation.get(key) or []:
            if p is None:
                continue
            if isinstance(p, dict):
                if "x" in p and "y" in p:
                    x, y = p["x"], p["y"]
                else:
                    x, y = p.get(0), p.get(1)
            else:
                x, y = (p[0], p[1]) if isinstance(p, (list, tuple)) and len(p) >= 2 else (None, None)
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                out.append((x, y))
        return out

    obstacles = set(collect("obstacles")) | set(collect("resource_obstacles"))
    resources = collect("resources") + collect("resource_cells") + collect("resource_locations")

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    tx, ty = ox, oy
    if resources:
        best = None
        for x, y in resources:
            d = md(sx, sy, x, y)
            if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
                best = (d, (x, y))
        tx, ty = best[1]

    moves = [(0, -1), (0, 0), (1, 0), (0, 1), (-1, 0)]
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = md(nx, ny, tx, ty)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]
    return best_move