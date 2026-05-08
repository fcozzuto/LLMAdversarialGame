def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if any(sx == r[0] and sy == r[1] for r in resources):
        return [0, 0]

    best = (0, 0)
    bestv = -10**18

    # small deterministic preference for breaking ties: move that reduces distance to opponent
    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            nx, ny, dxi, dyi = sx, sy, 0, 0

        # Heuristic: prioritize moves that create "temporal advantage" to at least one resource,
        # while lightly discouraging being farther overall.
        v = -md(nx, ny, ox, oy) * 0.03
        # row/col sweep response: add bonus for aligning with resources' row/col when opponent is far from them
        align_bonus = 0.0

        local_best = -10**18
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - myd  # >0 means we are closer (contend sooner)
            # Strongly reward creating a positive advantage, still allow contesting when behind.
            cand = adv * 100.0 - myd * 1.0
            if cand > local_best:
                local_best = cand

            # alignment: if we are near the resource's row/col and opponent isn't, help sweep response
            if (ny == ry or nx == rx) and od > myd:
                align_bonus += 1.0

        v += local_best + align_bonus * 2.0
        # discourage idle unless it is already best contending
        if dxi == 0 and dyi == 0:
            v -= 1.5

        if v > bestv:
            bestv = v
            best = (dxi, dyi)

    return [int(best[0]), int(best[1])]