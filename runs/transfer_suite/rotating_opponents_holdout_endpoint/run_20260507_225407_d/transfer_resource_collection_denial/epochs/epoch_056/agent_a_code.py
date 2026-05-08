def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not valid(tx, ty):
            continue
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer resources we can reach first; tie-break: closer to our target and different row
        key = (sd - od, sd, abs(ty - oy), abs(tx - sx))
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        # Opportunistic: move toward nearest valid cell in x (since opponent starts opposite corner)
        tx, ty = (0, 0) if (sx > w // 2) else (w - 1, h - 1)
        best = (tx, ty)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    bestm = (0, 0)
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        # Small pressure against opponent: avoid stepping into squares where opponent becomes strictly closer
        do = man(ox, oy, tx, ty)
        mk = (d, abs(ox - nx) + abs(oy - ny), (d - do))
        if bestmk is None or mk < bestmk:
            bestmk = mk
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]