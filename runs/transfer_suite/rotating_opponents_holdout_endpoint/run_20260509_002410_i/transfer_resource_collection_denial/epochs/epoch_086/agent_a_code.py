def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    resources = observation.get("resources") or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Pick a target resource we can reach at least as soon as opponent (prefer big advantage, then proximity).
    best = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        tx = int(r[0]); ty = int(r[1])
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obstacles:
            continue
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        # advantage favors us; add small bias for closer absolute distance.
        adv = do - ds
        score = (-adv, ds)  # prefer larger adv -> smaller -adv; then smaller ds
        if best is None or score < best[0]:
            best = (score, tx, ty, ds, do)
    if best is None:
        # No visible resources: head toward center to reduce opponent advantage
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_m = min(candidates, key=lambda t: (md(t[2], t[3], cx, cy), t[0] * t[0] + t[1] * t[1]))
        return [best_m[0], best_m[1]]

    _, tx, ty, ds, do = best
    # Choose move that decreases distance to target, but penalize steps that allow opponent to be closer after our move.
    best_move = None
    for dx, dy, nx, ny in candidates:
        ns = md(nx, ny, tx, ty)
        # approximate "race": compare opponent distance remains same (opponent moves later), use it as pressure
        race_pen = 0
        if do <= ns:
            race_pen = 20  # discourage paths where we're not on-time vs opponent
        step_cost = ns + race_pen
        # also lightly avoid moving directly away
        relx = 1 if tx > nx else (-1 if tx < nx else 0)
        rely = 1 if ty > ny else (-1 if ty < ny else 0)
        align = -((dx - relx) * (dx - relx) + (dy - rely) * (dy - rely))  # higher better
        key = (step_cost, -align, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)
    return [int(best_move[1]), int(best_move[2])]