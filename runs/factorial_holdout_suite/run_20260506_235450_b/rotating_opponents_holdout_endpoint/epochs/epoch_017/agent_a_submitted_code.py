def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for a in (observation.get("obstacles") or []):
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))
        elif isinstance(a, dict) and "x" in a and "y" in a:
            obs.add((int(a["x"]), int(a["y"])))

    def parse_xy(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict) and "x" in r and "y" in r:
            return int(r["x"]), int(r["y"])
        return None

    resources = []
    for r in observation.get("resources") or []:
        p = parse_xy(r)
        if p is not None:
            resources.append(p)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target = None
    best = 10**9
    for (rx, ry) in resources:
        d = man(sx, sy, rx, ry)
        if d < best or (d == best and (rx, ry) < target):
            best = d
            target = (rx, ry)

    if target is None:
        target = (ox, oy)

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = []
    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    if resources:
        best_movescore = 10**18
        best_move = moves[0]
        for dx, dy in sorted(moves):
            nx, ny = sx + dx, sy + dy
            score = (man(nx, ny, target[0], target[1]), man(ox, oy, target[0], target[1]), dx, dy)
            if score < best_movescore:
                best_movescore = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        best_movescore = -10**18
        best_move = moves[0]
        for dx, dy in sorted(moves):
            nx, ny = sx + dx, sy + dy
            score = (man(nx, ny, ox, oy), -man(nx, ny, target[0], target[1]), -dx, -dy)
            if score > best_movescore:
                best_movescore = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]