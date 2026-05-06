def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_sc = -10**18

    if not moves:
        return [0, 0]

    # If no resources visible, just drift to center.
    if not resources:
        cx = (w - 1) // 2
        cy = (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        if valid(sx + dx, sy):
            return [dx, 0]
        if valid(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    # Heuristic: for each resource, prefer moves that make us closer than opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        sc = 0.0

        # Strongly prefer states where we can contest (or beat) opponent on nearby resources.
        for rx, ry in resources:
            myd = king(nx, ny, rx, ry)
            opd = king(ox, oy, rx, ry)
            gap = opd - myd  # positive => we are closer than opponent
            d = myd if myd < opd else (opd if opd < myd else myd)
            # Weight closer-to-us resources more; make denial count more when opponent is also close.
            w1 = 4.0 / (1.0 + d)
            if gap > 0:
                sc += (1.0 + gap) * w1
            else:
                sc += gap * 0.9 * w1  # small penalty for giving up

            # Extra denial: if opponent is extremely close to a resource, avoid moves that keep us far.
            if opd <= 1 and myd >= opd + 1:
                sc -= 3.0 / (1.0 + myd)

        # Mild tie-breakers: reduce distance to the nearest resource; avoid moving toward opponent.
        my_near = min(king(nx, ny, rx, ry) for rx, ry in resources)
        opp_near = min(king(ox, oy, rx, ry) for rx, ry in resources)
        sc += 1.5 / (1.0 + my_near)
        sc -= 0.3 / (1.0 + opp_near)

        # Keep distance from opponent when contest is even.
        sc -= 0.05 * king(nx, ny, ox, oy)

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]