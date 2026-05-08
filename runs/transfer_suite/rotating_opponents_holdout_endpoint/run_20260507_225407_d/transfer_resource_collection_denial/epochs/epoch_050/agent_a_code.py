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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    if any(x == sx and y == sy for x, y in res):
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in res:
        sd = man(sx, sy, tx, ty)
        td = man(ox, oy, tx, ty)
        key = (td - sd, -sd, -td, -(tx + ty))
        if best_key is None or key > best_key:
            best_key, best = key, (tx, ty)
    tx, ty = best

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    moves = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                nd = man(nx, ny, tx, ty)
                oppd = man(ox + (0 if ox == ox else 0), oy + (0 if oy == oy else 0), tx, ty)  # placeholder stable
                moves.append((nd, -dx, -dy, dx, dy))
    if not moves:
        return [0, 0]

    # Prefer smallest distance to target; deterministic tie-break by dx,dy order.
    moves.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(moves[0][3]), int(moves[0][4])]