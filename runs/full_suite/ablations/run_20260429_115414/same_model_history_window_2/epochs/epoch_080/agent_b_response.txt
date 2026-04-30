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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        cx, cy = w // 2, h // 2
        best = None
        bestv = -10**18
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer
            center = -(abs(rx - cx) + abs(ry - cy))
            # Make it different: emphasize immediate race and de-emphasize far-away picks.
            v = adv * 1000 - sd * 20 + center * 3
            if v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Predict opponent's next best possible distance to our chosen target.
    def opp_best_next_dist():
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if ok(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
        return bestd if bestd != 10**9 else cheb(ox, oy, tx, ty)

    opp_next_d = opp_best_next_dist()

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        self_next_d = cheb(nx, ny, tx, ty)
        # Prefer maximizing our post-move advantage; tie-break by reducing our distance.
        score = (opp_next_d - self_next_d) * 1000 - self_next_d
        # Small deterministic tie-break: prefer moves with smaller dx, then smaller dy.
        score = score * 10 + (-(abs(dx) * 3 + abs(dy)))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]