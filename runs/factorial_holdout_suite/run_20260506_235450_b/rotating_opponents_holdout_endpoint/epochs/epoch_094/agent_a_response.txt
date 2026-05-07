def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for ob in obstacles:
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            x, y = int(ob[0]), int(ob[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    def parse_res(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict):
            if "x" in r and "y" in r:
                return int(r["x"]), int(r["y"])
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return None

    parsed = []
    for r in resources:
        p = parse_res(r)
        if p is not None:
            x, y = p
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                parsed.append((x, y))
    if not parsed:
        return [0, 0]

    best = None
    for (x, y) in parsed:
        sd = man(sx, sy, x, y)
        od = man(ox, oy, x, y)
        score = (od - sd, -sd, -(x + y), x, y)  # maximize od-sd; then minimize sd; then deterministic
        if best is None or score > best[0]:
            best = (score, x, y)

    tx, ty = best[1], best[2]

    moves = []
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            moves.append((dx, dy, man(nx, ny, tx, ty)))
    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (t[2], -abs(t[0]) - abs(t[1]), t[0], t[1]))
    # prefer strictly closer if possible
    cur_d = man(sx, sy, tx, ty)
    for dx, dy, nd in moves:
        if nd < cur_d:
            return [int(dx), int(dy)]
    dx, dy, _ = moves[0]
    return [int(dx), int(dy)]