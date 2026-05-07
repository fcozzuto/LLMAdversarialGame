def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_val = -10**30

    # Prefer moves that create a distance advantage to close/far resources and avoid getting closer to obstacles.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        # immediate safety: penalize moves adjacent to obstacles (soft)
        for ax, ay in obstacles:
            if cheb(nx, ny, ax, ay) <= 1 and (ax != nx or ay != ny):
                val -= 2

        # goal race over remaining resources
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Big reward if we are closer than opponent; otherwise reward reducing gap.
            gap = opd - myd
            # Encourage moving toward nearer contested targets (myd small is good), and discourage moving away.
            val += gap * 50
            val += (8 - myd) * 3

            # If this move reaches a resource this turn, heavily prioritize it.
            if myd == 0:
                val += 10**6

        # small preference to continue toward more valuable regions: tie-break by larger total closeness
        closeness_sum = 0
        for rx, ry in resources:
            closeness_sum += (10 - cheb(nx, ny, rx, ry))
        val += closeness_sum

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best