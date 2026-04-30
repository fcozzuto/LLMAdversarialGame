def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Deterministic center drift with slight anti-opponent bias
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, int(round(cx)), int(round(cy))) - 0.1 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Evaluate each move by choosing the resource that gives maximal advantage now
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_target_adv = -10**18
        best_target_dist = 10**9
        best_target_tie = None

        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer than opponent
            # tie-break: prefer shorter self distance, then lexicographic
            if adv > best_target_adv or (adv == best_target_adv and (sd < best_target_dist or (sd == best_target_dist and (rx, ry) < best_target_tie))):
                best_target_adv = adv
                best_target_dist = sd
                best_target_tie = (rx, ry)

        # Encourage grabbing instantly and discourage moving away from the currently advantaged target
        instant = 20 if (nx, ny) in resources else 0
        opp_pressure = 0.15 * cheb(nx, ny, ox, oy)
        # If we are not closer to any resource, still move toward the closest one deterministically
        closest_self = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
        v = 3.0 * best_target_adv - opp_pressure + instant - 0.35 * closest_self
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]