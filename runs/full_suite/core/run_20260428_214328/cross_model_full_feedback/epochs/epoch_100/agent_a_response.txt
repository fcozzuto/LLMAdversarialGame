def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b): return abs(a[0] - b[0]) if abs(a[0] - b[0]) >= abs(a[1] - b[1]) else abs(a[1] - b[1])
    def sign(t): return 0 if t == 0 else (1 if t > 0 else -1)

    me = (sx, sy)
    opp = (ox, oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a resource that we can reach sooner than opponent, with tie-breakers to keep pressure.
    target = None
    best = -10**9
    if resources:
        for r in resources:
            ds = cheb(me, r)
            do = cheb(opp, r)
            # Prefer larger gap (op slower), then closer to us; discourage very far targets.
            score = (do - ds) * 100 - ds * 3 - (abs(r[0] - (w // 2)) + abs(r[1] - (h // 2)))
            if score > best:
                best = score
                target = r

    # If no resources visible, drift toward opponent's direction to contest center-ish.
    if target is None:
        dx = sign(ox - sx)
        dy = sign(oy - sy)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            return [dx, dy]
        # fallback: try any safe move
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    tx, ty = target
    # Primary step: greedy toward target.
    dx0, dy0 = sign(tx - sx), sign(ty - sy)
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        ds = cheb((nx, ny), target)
        # Also consider how the move affects opponent's ability to get that target next.
        dop = cheb(opp, target)
        # If we move closer than opponent would "on their turn", keep it; otherwise avoid giving them a fast grab.
        give = ds - dop
        # Slight tie-break to avoid walking into corners unnecessarily.
        center = abs(nx - (w // 2)) + abs(ny - (h // 2))
        # Prefer reducing distance; penalize moving away from target direction.
        dir_pen = abs(nx - sx - dx0) + abs(ny - sy - dy0)
        score = (-ds) * 10 - give * 2 - center - dir_pen
        candidates.append((score, dx, dy))

    if candidates:
        candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
        return [candidates[0][1], candidates[0][2]]

    return [0, 0]