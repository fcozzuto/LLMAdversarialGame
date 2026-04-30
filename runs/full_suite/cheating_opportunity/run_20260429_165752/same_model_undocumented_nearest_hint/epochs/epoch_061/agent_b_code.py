def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def pick_target():
        if not resources:
            return None
        best = None
        bestv = None
        for x, y in resources:
            d_me = cheb(sx, sy, x, y)
            d_op = cheb(ox, oy, x, y)
            # Prefer resources we can reach sooner; tie-break deterministically by coords.
            # Add slight preference for top-left to avoid oscillations.
            score = (d_me - d_op, d_me, x + 0.01 * y)
            if best is None or score < bestv:
                best = (x, y)
                bestv = score
        return best

    def step_towards(tx, ty):
        bestm = (0, 0)
        bestscore = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Primary: reduce distance to target.
            d = cheb(nx, ny, tx, ty)
            # Secondary: avoid moving into cells where opponent is closer to the target.
            do = cheb(ox, oy, tx, ty)
            threat = cheb(nx, ny, ox, oy)
            cand = (d, -do, threat)
            if bestscore is None or cand < bestscore:
                bestscore = cand
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    target = pick_target()
    if target is None:
        # No visible resources: drift deterministically toward center while avoiding obstacles.
        cx, cy = (W - 1) // 2, (H - 1) // 2
        return step_towards(cx, cy)

    return step_towards(target[0], target[1])