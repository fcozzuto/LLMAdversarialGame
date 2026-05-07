def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                targets.append((x, y))
    if not targets:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [(dx, dy) for (dx, dy) in moves if inb(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    # Score each move by best resource advantage (how much we close vs opponent)
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Find a resource we can potentially take sooner than opponent
        val = None
        for rx, ry in targets:
            ds0 = manh(sx, sy, rx, ry)
            ds1 = manh(nx, ny, rx, ry)
            do0 = manh(ox, oy, rx, ry)
            do1 = manh(ox, oy, rx, ry)  # opponent position unchanged this turn
            # Prefer resources where we reduce distance more than opponent is already advantaged
            score = (do0 - ds1) - (do0 - ds0)  # effectively (ds0 - ds1)
            # Also strongly prefer increasing relative advantage to current closest opponent
            rel = (do0 - ds1) - (do0 - do1)
            cand = (score, rel, -ds1, -manh(nx, ny, ox, oy))
            if val is None or cand > val:
                val = cand
        # Tie-break deterministically: prefer (0,0) then smallest abs dx then smallest abs dy then direction order
        key = (val, -abs(dx), -abs(dy), moves.index((dx, dy)))
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]