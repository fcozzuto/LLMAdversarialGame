def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or [])]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_risk(x, y):
        r = 0
        for ax in (-1, 0, 1):
            nx = x + ax
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0: 
                    continue
                if (nx, y + ay) in obst:
                    r += 2
        if x == 0 or x == w - 1 or y == 0 or y == h - 1:
            r += 0.25
        return r

    if not resources:
        tx, ty = w // 2, h // 2
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                v = -cheb(nx, ny, tx, ty) - 0.5 * obstacle_risk(nx, ny)
                if v > best[0]:
                    best = (v, dx, dy)
        return [best[1], best[2]]

    bestv, bestdx, bestdy = -10**18, 0, 0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        risk = obstacle_risk(nx, ny)
        # Evaluate the best resource action after this move.
        v = -0.8 * risk
        for rx, ry in resources:
            dself = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # Prefer resources where we are (or become) earlier.
            # Being strictly earlier is strongly rewarded; being later is penalized.
            lead = dop - dself
            cur = 1.6 * lead - 0.15 * dself
            # Small preference for resources nearer to the center late game.
            if observation.get("remaining_resource_count", 9999) <= 4:
                cx, cy = w // 2, h // 2
                cur += 0.03 * (cheb(rx, ry, cx, cy) * -1)
            if cur > v:
                v = cur - 0.5 * risk
        if v > bestv:
            bestv, bestdx, bestdy = v, dx, dy

    return [bestdx, bestdy]