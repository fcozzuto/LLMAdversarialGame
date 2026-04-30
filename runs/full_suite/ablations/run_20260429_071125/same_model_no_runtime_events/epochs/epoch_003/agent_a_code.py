def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                v = -cheb(nx, ny, ox, oy)
                if v > bestv or (v == bestv and (dx, dy) < best):
                    bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best_target = None
    bestv = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; also deny opponent when we're not first.
        score = (do - ds) * 10 - ds
        # Mild incentive for nearer resources to speed up tempo.
        score += -0.5 * (abs(rx - ox) + abs(ry - oy)) * 0.0
        if score > bestv:
            bestv = score
            best_target = (rx, ry)

    tx, ty = best_target
    # Greedy single-step toward chosen target; if blocked, pick best alternative step.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Recompute relative advantage for this next position.
        do_next = cheb(ox, oy, tx, ty)
        advantage = do_next - d
        v = advantage * 10 - d
        # Tie-break deterministically: prefer smaller (abs dx + abs dy), then lexicographic.
        steps = abs(dx) + abs(dy)
        v -= steps * 0.01
        if v > bestv or (v == bestv and (steps, dx, dy) < (abs(best[0]) + abs(best[1]), best[0], best[1])):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]