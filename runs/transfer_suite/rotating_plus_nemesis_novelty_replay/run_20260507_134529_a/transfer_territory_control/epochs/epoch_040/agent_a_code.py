def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)
    def best_target(cells):
        best = (sx, sy)
        best_d = 10**9
        for tx, ty in cells:
            if (tx, ty) in obstacles:
                continue
            d = md(sx, sy, tx, ty)
            if d < best_d:
                best_d = d
                best = (tx, ty)
        return best

    target_pool = unclaimed or resources or self_terr or {(sx, sy)}
    tx, ty = best_target(target_pool)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_terr:
            score = -10**12
        else:
            score = 0
            score += 2000 if (nx, ny) in resources else 0
            score += 1000 if (nx, ny) in unclaimed else 0
            score += 20 if (nx, ny) in self_terr else 0
            score += -(md(nx, ny, tx, ty))
            score += md(nx, ny, ox, oy) * 2
            score -= (1 if dx == 0 and dy == 0 else 0) * 3
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]