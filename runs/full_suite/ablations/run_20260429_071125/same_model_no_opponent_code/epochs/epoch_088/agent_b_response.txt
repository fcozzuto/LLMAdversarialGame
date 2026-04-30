def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick a target resource we can reach sooner than the opponent.
    best = None
    best_score = -10**18
    for x, y in resources:
        myd = cheb(sx, sy, x, y)
        opd = cheb(ox, oy, x, y)
        # Primary: how much earlier we are than opponent; Secondary: be closer overall.
        score = (opd - myd) * 100 - myd
        # If we are about to be overtaken, still grab if close enough.
        if myd <= 1 and opd > myd:
            score += 500
        if opd <= 1 and myd > opd:
            score -= 400
        if score > best_score:
            best_score = score
            best = (x, y)

    tx, ty = best

    # Avoid obstacles by choosing the best among legal step deltas.
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_mscore = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        # Encourage reducing distance to target and slightly steering away from obstacles by preferring open area.
        openness = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
                openness += 1
        mscore = -myd2 * 100 + openness
        # If opponent is very close to the target, reduce our distance even if it means staying.
        if cheb(ox, oy, tx, ty) <= 2:
            mscore += (2 - myd2) * 30
        if mscore > best_mscore:
            best_mscore = mscore
            best_move = [dx, dy]

    return best_move