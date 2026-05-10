def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = 0, h - 1
        for c in [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]:
            if cheb(c[0], c[1], ox, oy) > cheb(tx, ty, ox, oy):
                tx, ty = c[0], c[1]
        best, bestm = -10**9, [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty) + 0.01 * cheb(nx, ny, ox, oy)
            if score > best:
                best, bestm = score, [dx, dy]
        return bestm

    # Choose target resource where we are at least as close as opponent (tie favored), then maximize margin after our move.
    best_score, best_move = -10**18, [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Select best resource for this hypothetical next position.
        local_best = (-10**18, None, None)  # (score, sd, od)
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where self is closer; if equal, prefer absolute closeness; break ties deterministically.
            # Also slight anti-block: if opponent can be closer, still allow when self is much closer.
            score = (od - sd) * 1000 - sd * 3 + (od - sd == 0) * 5 - (rx * 0.001 + ry * 0.0001)
            if score > local_best[0] or (score == local_best[0] and (sd, od, rx, ry) < (local_best[1], local_best[2], 0, 0)):
                local_best = (score, sd, od)

        # Add small preference to reduce our distance to the chosen resource and avoid moving away.
        sd = local_best[1]
        od = local_best[2]
        # Reward if we keep/establish an advantage after the move; penalize if we worsen it.
        self_before_best_sd = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
        self_after_cost = sd
        adv = (od - sd)
        score2 = local_best[0] + adv * 2 - self_after_cost * 0.5 - cheb(nx, ny, sx, sy) * 0.001 - self_before_best_sd * 0.0

        if score2 > best_score or (score2 == best_score and [dx, dy] < best_move):
            best_score, best_move = score2, [dx, dy]

    return [int(best_move[0]), int(best_move[1])]