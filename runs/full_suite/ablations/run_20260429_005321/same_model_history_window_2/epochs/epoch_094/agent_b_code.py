def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w - 1, h - 1), (0, 0), (0, h - 1), (w - 1, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    opp_eff = []
    for tx, ty in resources:
        d = cheb(ox, oy, tx, ty)
        if d > 0:
            d -= 1  # assume opponent can also step closer
        opp_eff.append(d)

    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = 0
        for i, (tx, ty) in enumerate(resources):
            myd = cheb(nx, ny, tx, ty)
            oppd = opp_eff[i]
            # Prefer resources we can reach sooner; otherwise reduce being behind.
            adv = (oppd - myd)
            # Higher reward for closer target when contested.
            clos = 0 if myd == 0 else 1.0 / (1 + myd)
            val += (adv * 10.0) + (clos * 3.0)
        # Minor deterministic tie-break: prefer moves that reduce sum-to-center distance and avoid staying if equal.
        center = (w - 1) / 2.0
        tie = - (abs(nx - center) + abs(ny - center)) * 0.01 - (0 if (dx == 0 and dy == 0) else 0)
        val += tie
        if val > bestv:
            bestv = val
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]