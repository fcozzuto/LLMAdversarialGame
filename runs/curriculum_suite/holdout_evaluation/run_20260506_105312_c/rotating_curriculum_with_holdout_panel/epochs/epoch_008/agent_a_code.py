def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    # Precompute a deterministic target ordering score to add stability.
    # Prefer resources that are "safer": you reach earlier and opponent is not too close.
    scored_res = []
    for rx, ry in resources:
        myd0 = cheb(sx, sy, rx, ry)
        opd0 = cheb(ox, oy, rx, ry)
        # earlier reach strongly favored; if opponent closer, heavily penalize
        safety = (opd0 - myd0) * 25 - myd0
        # slight preference toward resources not immediately on opponent trajectory distance
        close = 3 - min(3, cheb(ox, oy, rx, ry))
        scored_res.append((-(safety * 10 + close), rx, ry))
    scored_res.sort()
    # Evaluate candidate moves: maximize immediate improvement on top K resources.
    K = 4 if len(scored_res) >= 4 else len(scored_res)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0
        # Edge/corner deterrence to reduce oscillations
        if (nx == 0 or nx == w - 1) and (ny == 0 or ny == h - 1):
            v -= 4

        for i in range(K):
            _, rx, ry = scored_res[i]
            myd1 = cheb(nx, ny, rx, ry)
            opd1 = cheb(ox, oy, rx, ry)
            myd0 = cheb(sx, sy, rx, ry)
            # If we are (or become) the earlier arriver, reward heavily
            arrive_adv = (opd1 - myd1)
            progress = myd0 - myd1
            v += arrive_adv * 30 + progress * 8 - myd1
            # If opponent is about to deny (very close), reduce
            if opd1 <= 1:
                v -= 60
            # Small deterministic tiebreaker based on coordinates
            v += (rx * 3 + ry) * 0.01

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]