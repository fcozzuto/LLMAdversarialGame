def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target we can reach sooner (tie is still valuable).
    best = None
    best_gain = -10**9
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Gain favors contested targets and keeps closer to them.
        gain = (opd - myd) * 10 - myd
        # Small deterministic preference: closer to our current quadrant corner (lower x then y).
        gain -= (tx * 0.001 + ty * 0.0001)
        if best is None or gain > best_gain:
            best_gain = gain
            best = (tx, ty)

    tx, ty = best

    # One-step lookahead: pick move that minimizes distance to target, with tie-breakers.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in blocked:
                continue
            d = cheb(nx, ny, tx, ty)
            # Discourage moves that let opponent get closer to the same target.
            opp_d = cheb(ox, oy, tx, ty)
            myd = cheb(sx, sy, tx, ty)
            # Approx: prefer reducing my distance more than any likely opponent advantage (opd fixed).
            score = d * 100 - (opp_d - myd) * 5
            # Deterministic tie-break: prefer cardinal directions, then negative dx, then negative dy.
            score += (0 if dx != 0 and dy == 0 else 1)  # diagonals slightly worse
            score += (0 if dx == -1 else 1) * 0.01
            score += (0 if dy == -1 else 1) * 0.001
            moves.append((score, dx, dy))

    moves.sort(key=lambda t: t[0])
    return [int(moves[0][1]), int(moves[0][2])]