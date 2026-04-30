def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx >= dy else dy

    def neigh_moves(x, y):
        ms = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if dx == 0 and dy == 0:
                    ms.append((0, 0, x, y))
                elif inb(nx, ny) and (nx, ny) not in obstacles:
                    ms.append((dx, dy, nx, ny))
        return ms

    if not resources:
        # Head toward opponent corner (0,0 if inside grid), otherwise toward farthest corner by chebyshev.
        tx, ty = 0, 0
        best = (0, 0, -10**9)
        for dx, dy, nx, ny in neigh_moves(sx, sy):
            v = -cheb(nx, ny, tx, ty)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    # Decide mode: deny/intercept if opponent is closer to the best remaining resource.
    my_best = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
    opp_best = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
    deny_mode = opp_best < my_best

    # Pick a target resource deterministically maximizing denial advantage.
    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # tie-break: prefer smaller md, then lexicographically smaller resource
        score = (od - md) * 10 - md
        if deny_mode:
            score += 100  # emphasize denying when behind
        if (score > best_score) or (score == best_score and (md < cheb(sx, sy, best_r[0], best_r[1]) or (md == cheb(sx, sy, best_r[0], best_r[1]) and (rx, ry) < best_r))):
            best_score = score
            best_r = (rx, ry)

    rx, ry = best_r

    # If denying, also try to stand on the "approach line" toward that resource relative to opponent.
    # Choose a move that minimizes our distance to the resource, but penalize moving closer to opponent if they are already closer.
    best_move = (0, 0, -10**18)
    for dx, dy, nx, ny in neigh_moves(sx, sy):
        myd = cheb(nx, ny, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        # If opponent is closer to this resource, prefer moves that increase their distance from their current position.
        v = -myd
        if deny_mode and cheb(ox, oy, rx, ry) <= cheb(sx, sy, rx, ry):
            v += (cheb(ox, oy, rx, ry) - cheb(ox, oy, nx, ny)) * 0.1
        # Avoid stepping into positions that are worse for us while not improving denial.
        if deny_mode:
            v += (oppd - cheb(ox, oy, rx, ry))  # keep deterministic structure
        # Tie-break: prefer move that is lexicographically smallest among best values.
        if (v > best_move[2]) or (v == best_move[2] and (dx, dy) < (best_move[0], best_move[1])):
            best_move = (dx, dy, v)

    return [int(best_move[0]), int(best_move[1])]