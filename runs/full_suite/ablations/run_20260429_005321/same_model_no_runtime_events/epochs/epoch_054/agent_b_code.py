def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        best = None
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # keep distance from opponent while staying mobile toward center
            dpo = cheb(nx, ny, ox, oy)
            dc = cheb(nx, ny, w // 2, h // 2)
            v = dpo * 2 - dc
            if v > bestv:
                bestv, best = v, (dx, dy)
        return list(best) if best is not None else [0, 0]

    # If possible, move to a resource where we can beat the opponent, otherwise pick least-losing + avoid getting too close.
    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        dme0 = cheb(nx, ny, ox, oy)
        # Slightly discourage stepping into the same cell as opponent in next move (not allowed anyway).
        avoid = -dme0

        # Value resource by "how much closer we are than opponent after this move"
        # (bigger is better). Add small tie-break toward nearest.
        score = -10**18
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            v = (dop - dme) * 3 - dme  # prioritize resources we can arrive at sooner
            if v > score:
                score = v

        # If we can't beat anyone (score <= 0), still prefer maximizing (dop - dme) and staying away from opponent.
        # This inherently differs from prior greedy-only policies that follow a fixed target.
        vtot = score + avoid * 0.2
        if vtot > bestv:
            bestv, best = vtot, (dx, dy)

    return list(best) if best is not None else [0, 0]