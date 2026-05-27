def choose_move(observation):
    def i(v, d=0):
        try:
            return int(v if v is not None else d)
        except:
            return d

    def p(v):
        if isinstance(v, dict):
            return i(v.get("x", v.get("col", 0))), i(v.get("y", v.get("row", 0)))
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return i(v[0]), i(v[1])
        return 0, 0

    def s(v):
        r = set()
        for c in v or []:
            r.add(p(c))
        return r

    w = i(observation.get("grid_width", observation.get("width", 0)))
    h = i(observation.get("grid_height", observation.get("height", 0)))
    sx, sy = p(observation.get("self_position", (0, 0)))
    ox, oy = p(observation.get("opponent_position", (0, 0)))
    res = list(observation.get("resources", []) or [])
    bad = s(observation.get("obstacles", [])) | s(observation.get("self_path", [])) | s(observation.get("opponent_path", []))
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in bad

    def dist(a, b, x, y):
        return abs(a - x) + abs(b - y)

    best = None
    for tx, ty in res:
        d = dist(sx, sy, tx, ty)
        if best is None or d < best[0] or (d == best[0] and (tx, ty) < best[1]):
            best = (d, (tx, ty))

    if best is not None:
        tx, ty = best[1]
        cand = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                cand.append((dist(nx, ny, tx, ty), dx, dy, nx, ny))
        if cand:
            cand.sort()
            return [cand[0][1], cand[0][2]]

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            cand.append((dist(nx, ny, ox, oy), -abs(dx) - abs(dy), dx, dy))
    if cand:
        cand.sort()
        return [cand[0][2], cand[0][3]]
    return [0, 0]
