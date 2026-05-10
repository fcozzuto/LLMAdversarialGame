def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                valid_res.append((x, y))
    if not valid_res:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Choose resource by advantage, with deterministic tie-breaks.
    best = None
    for rx, ry in valid_res:
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        margin = oppd - myd  # positive means we're closer
        center = abs(rx - cx) + abs(ry - cy)
        # Small bias toward moving "forward" in time: prefer closer even if margin similar.
        key = (margin, -myd, -center, -(rx * 31 + ry * 17))
        if best is None or key > best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    # Move one step toward target, avoid obstacles; deterministic among equal scores.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obs:
                    moves.append((dx, dy))
    if not moves:
        return [0, 0]

    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = man(nx, ny, tx, ty)
        # Prefer reducing distance; also prefer not letting opponent get closer to same target.
        opp_next = man(ox, oy, tx, ty)
        # If opponent already very close, prioritize our own progress more.
        opp_pressure = 1 if opp_next <= 2 else 0
        score = (-d, opp_pressure * (-(opp_next - d)), -abs(nx - cx) - abs(ny - cy), -(dx * 3 + dy))
        if bestm is None or score > bestm[0]:
            bestm = (score, dx, dy)

    return [int(bestm[1]), int(bestm[2])]