def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry):
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dx, dy in dirs:
            if inb(x + dx, y + dy):
                c += 1
        return c

    # If no resources, just increase mobility and move toward center-ish.
    if not resources:
        best = None
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = mobility(nx, ny) - 0.01 * cheb(nx, ny, w // 2, h // 2)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    # Target: resource that we can reach earlier than opponent, considering diminishing returns.
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_best_adv = -10**9
        my_best_dist = 10**9
        opp_best_dist = 10**9

        # Evaluate advantage relative to each resource (deterministic scan order).
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_my  # positive means we are closer or tie
            # prefer closer to a resource we can plausibly contest; add small bias to smaller absolute distance
            score = adv * 10 - d_my
            if score > my_best_adv:
                my_best_adv = score
                my_best_dist = d_my
                opp_best_dist = d_op
        # Prefer moves that also reduce opponent "pressure" on that contested resource.
        # Also consider mobility to avoid getting trapped near obstacles.
        v = my_best_adv + 0.5 * (opp_best_dist - my_best_dist) + 0.2 * mobility(nx, ny)
        # Small deterministic center preference to break ties.
        v -= 0.01 * cheb(nx, ny, w // 2, h // 2)

        candidates.append((v, dx, dy))

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])] if candidates else [0, 0]