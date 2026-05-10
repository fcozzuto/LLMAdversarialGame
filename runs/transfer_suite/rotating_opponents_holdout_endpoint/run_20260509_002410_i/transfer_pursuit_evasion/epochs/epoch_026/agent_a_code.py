def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    self_score = 0
    scores = observation.get("scores")
    if isinstance(scores, (list, tuple)) and len(scores) >= 2:
        self_score = scores[0] if scores[0] is not None else 0
        opp_score = scores[1] if scores[1] is not None else 0
    elif isinstance(scores, dict):
        vals = list(scores.values())
        self_score = vals[0] if vals else 0
        opp_score = vals[1] if len(vals) > 1 else 0
    else:
        opp_score = 0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        tx, ty = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
        best = None
        best_i = 0
        for i, (dx, dy) in enumerate(moves):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            sc = -d
            if best is None or sc > best:
                best, best_i = sc, i
        return [moves[best_i][0], moves[best_i][1]]

    target_toward = (ox, oy) if self_score <= opp_score else (ox, oy)
    best = None
    best_i = 0
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        do = man(nx, ny, ox, oy)
        sc = -do if self_score <= opp_score else do
        if best is None or sc > best:
            best, best_i = sc, i
    return [moves[best_i][0], moves[best_i][1]]