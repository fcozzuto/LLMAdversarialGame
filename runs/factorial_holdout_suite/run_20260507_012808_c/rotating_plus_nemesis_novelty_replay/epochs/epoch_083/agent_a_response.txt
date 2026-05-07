def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        if sx < tx: dx = 1
        elif sx > tx: dx = -1
        else: dx = 0
        if sy < ty: dy = 1
        elif sy > ty: dy = -1
        else: dy = 0
        return [dx, dy]

    resources.sort(key=lambda p: (p[0], p[1]))
    best = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        myd = manh(rx, ry, sx, sy)
        opd = manh(rx, ry, ox, oy)
        # Advantage: prefer resources where I'm closer; also slight preference for nearer targets.
        val = (opd - myd) * 100 - myd
        # If opponent can reach in same/less steps, try to choose something else.
        if opd <= myd:
            val -= 50
        # Deterministic micro-tiebreaker.
        val -= (rx * 8 + ry)
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    best_move = (0, 0)
    best_dist = 10**18
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            if (nx, ny) in obstacles:
                continue
            d = manh(nx, ny, tx, ty)
            if d < best_dist:
                best_dist = d
                best_move = (dx, dy)

    if best_move == (0, 0) and (sx + 0, sy + 0) not in obstacles:
        # If all safe moves were blocked by obstacles, allow the least-bad step (including obstacle-step).
        best_dist = 10**18
        for dx, dy in deltas:
            nx = sx + dx
            ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                d = manh(nx, ny, tx, ty)
                if d < best_dist:
                    best_dist = d
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]