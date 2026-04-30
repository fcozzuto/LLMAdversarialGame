def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # Head toward center while avoiding opponent a bit
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            v = cheb(nx, ny, tx, ty) + 0.25 * cheb(nx, ny, ox, oy)
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    # Pre-score resources by "control": prefer where we're closer than opponent
    res_scores = []
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        dop = cheb(ox, oy, rx, ry)
        # add small preference for being on resource soon
        # higher is better; invert later by minimizing
        score = (dop - dme) * 1.5 - dme * 0.15 - 0.02 * (abs(rx - ox) + abs(ry - oy))
        res_scores.append((score, rx, ry))
    res_scores.sort(reverse=True)

    best = None
    for dx, dy, nx, ny in moves:
        # Evaluate best reachable resource from the next position
        best_target = -10**9
        for score, rx, ry in res_scores[:5]:
            # penalty if moving would force away from that resource
            dnext = cheb(nx, ny, rx, ry)
            # recompute competition margin approximately (opponent one step)
            dop_next = cheb(ox, oy, rx, ry)
            target = (dop_next - dnext) * 1.5 - dnext * 0.15 + score * 0.02
            best_target = target if target > best_target else best_target

        # Avoid stepping adjacent to obstacles too often and avoid opponent proximity
        obst_adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obs:
                    obst_adj += 1
        opp_pen = 0.35 * (3 - min(3, cheb(nx, ny, ox, oy)))  # closer opponent => bigger penalty

        # Lower is better for selection
        v = -best_target + 0.02 * obst_adj + opp_pen
        if best is None or v < best[0]:
            best = (v, dx, dy)

    return [best[1], best[2]]