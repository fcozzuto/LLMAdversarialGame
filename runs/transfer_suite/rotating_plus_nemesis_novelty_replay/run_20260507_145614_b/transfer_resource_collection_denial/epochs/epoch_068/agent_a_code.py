def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]
    if any(sx == r[0] and sy == r[1] for r in resources):
        return [0, 0]

    opp_target = min(resources, key=lambda r: dist(ox, oy, r[0], r[1]))
    opp_dist_best = dist(ox, oy, opp_target[0], opp_target[1])

    best = None
    best_val = -10**9
    ti = observation.get("turn_index", 0) or 0
    for dxi, dyi in moves:
        nx, ny = sx + dxi, sy + dyi
        if not inb(nx, ny):
            nx, ny = sx, sy
            dxi, dyi = 0, 0

        # Main objective: maximize advantage at picking the best resource.
        val = 0
        for r in resources:
            rx, ry = r[0], r[1]
            myd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Reward being earlier, penalize being later, slight preference for nearer totals.
            val += (od - myd) * 3 - (myd + od) * 0.2

        # Strategic deny: if opponent is close to a particular resource, try to increase its distance to it.
        deny_myd = dist(nx, ny, opp_target[0], opp_target[1])
        deny_gain = (deny_myd - opp_dist_best) * 1.5
        val += deny_gain

        # Deterministic tie-break: prefer moves with smaller manhattan-ish toward opponent's nearest or rotate with turn_index.
        tie = 0.01 * (abs(nx - ox) + abs(ny - oy)) + (0.0001 * ((dxi + 2) * 7 + (dyi + 1) * 13 + (ti % 5)))
        val -= tie

        if val > best_val:
            best_val = val
            best = (dxi, dyi)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]