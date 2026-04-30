def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    def eval_target(tx, ty):
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources we can reach strictly earlier; penalize contested ones.
        lead = do - ds
        # Add slight preference for nearer targets when lead ties.
        return lead * 1000 - ds

    if resources:
        best = resources[0]
        bestv = eval_target(best[0], best[1])
        for tx, ty in resources[1:]:
            v = eval_target(tx, ty)
            if v > bestv or (v == bestv and (tx, ty) < best):
                bestv = v
                best = (tx, ty)
        tx, ty = best
    else:
        # No visible resources: drift toward opponent to force intercept corridors.
        tx, ty = ox, oy

    # Choose move that reduces distance to target; if target step blocked, use best legal alternative.
    bestm = (0, 0, sx, sy)
    bestscore = -10**18
    # Compute whether moving would "compete": if we end adjacent/at same time as opponent, add pressure.
    for dx, dy, nx, ny in legal:
        dsn = cheb(nx, ny, tx, ty)
        don = cheb(ox, oy, tx, ty)
        self_gain = (don - dsn) * 1000
        # If opponent is very close to target, prioritize denying by approaching anyway.
        deny = 80 if don <= 1 else 0
        # Tie-break: closer to target, then lexicographic by move.
        score = self_gain + deny - dsn * 5 - (abs(nx - sx) + abs(ny - sy)) * 0.1
        if score > bestscore or (score == bestscore and (dx, dy) < (bestm[0], bestm[1])):
            bestscore = score
            bestm = (dx, dy, nx, ny)

    return [int(bestm[0]), int(bestm[1])]