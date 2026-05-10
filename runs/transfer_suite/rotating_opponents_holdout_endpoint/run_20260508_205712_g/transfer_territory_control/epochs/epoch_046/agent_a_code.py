def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def to_xy(p):
        if not p:
            return (0, 0)
        try:
            return (int(float(p[0])), int(float(p[1])))
        except Exception:
            return (0, 0)

    sx, sy = to_xy(observation.get("self_position"))
    ox, oy = to_xy(observation.get("opponent_position"))

    def add_cells(key):
        out = set()
        for t in observation.get(key) or []:
            try:
                x = int(float(t[0])); y = int(float(t[1]))
            except Exception:
                continue
            out.add((x, y))
        return out

    obstacles = add_cells("obstacles")
    unclaimed = add_cells("unclaimed_cells")
    self_terr = add_cells("self_territory")

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 10
        if (nx, ny) in self_terr:
            score += 3
        score -= dist2(nx, ny, ox, oy)
        if (nx, ny) in unclaimed:
            score -= dist2(nx, ny, sx, sy) // 2
        if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]