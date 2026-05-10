def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    best = None
    best_move = [0, 0]
    cur_dist2 = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if blocked(nx, ny):
            continue

        mdx, mdy = nx - ox, ny - oy
        dist2 = mdx * mdx + mdy * mdy
        edge = 1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0

        # obstacle proximity penalty to avoid getting boxed in
        prox = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if blocked(ax, ay):
                    prox += 1

        if is_evader:
            # maximize survival: keep distance, prefer edges/corners, avoid prox obstacles
            score = dist2 * 10.0 + edge * 3.0 - prox * 2.5
            # small nudge to move away rather than toward
            score += (dist2 - cur_dist2) * 0.8
        else:
            # pursuer: minimize distance, prefer reducing it strongly, avoid prox obstacles
            score = -dist2 * 10.0 - prox * 2.5
            score += (cur_dist2 - dist2) * 2.0
            # encourage line toward opponent
            score += (-abs(nx - ox) - abs(ny - oy)) * 0.2

        # deterministic tie-break by fixed deltas order
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]