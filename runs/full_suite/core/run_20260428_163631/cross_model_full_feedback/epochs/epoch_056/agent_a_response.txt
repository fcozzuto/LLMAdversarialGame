def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # If no resources, deterministically drift away from opponent
        best = legal[0]; bestv = -10**18
        for dx, dy, nx, ny in legal:
            d = dist((nx, ny), (ox, oy))
            v = d
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    my = (sx, sy); op = (ox, oy)

    # Pick a target: prefer resources where we are closer than opponent; otherwise closest overall.
    best_target = None
    best_adv = -10**18
    for r in resources:
        dmy = dist(my, r)
        dop = dist(op, r)
        adv = dmy - dop  # <=0 is good
        # prioritize strongly advantaged targets, then smaller distance
        v = -1000 * (adv > 0) - adv - 0.01 * dmy
        if v > best_adv:
            best_adv = v
            best_target = r

    tx, ty = best_target

    # Evaluate moves: advance toward target, increase advantage, avoid getting too close to opponent.
    best = legal[0]; bestv = -10**18
    for dx, dy, nx, ny in legal:
        nxt = (nx, ny)
        d1 = dist(nxt, (tx, ty))
        d0 = dist(my, (tx, ty))
        mydist = dist(nxt, (tx, ty))
        opdist = dist(op, (tx, ty))
        opp_to_nxt = dist(nxt, op)

        # Advantage: how much closer we are to target relative to opponent's current distance
        adv_now = mydist - opdist
        # Progress bonus uses reduction in distance to target
        progress = d0 - d1

        # Repulsion (avoid allowing opponent to "catch up" on same cell region)
        repel = -0.15 / (1 + opp_to_nxt)

        # Slight preference to stay mobile (reduce being stuck) by encouraging staying away from obstacles-adjacent cells
        adj_obs = 0
        for ex, ey in ((nx-1, ny),(nx+1, ny),(nx, ny-1),(nx, ny+1)):
            if (ex, ey) in obstacles:
                adj_obs += 1
        stuck_pen = -0.08 * adj_obs

        v = 3.0 * progress - 1.2 * adv_now + repel + stuck_pen
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]