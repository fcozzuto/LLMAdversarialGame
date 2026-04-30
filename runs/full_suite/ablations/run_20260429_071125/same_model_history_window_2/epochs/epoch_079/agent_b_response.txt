def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_prox(x, y):
        if not obstacles:
            return 0
        best = 999
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best

    if not resources:
        return [0, 0]

    # Target: favor resources where we can beat the opponent (largest distance advantage).
    best_t = resources[0]
    best_adv = cheb(ox, oy, resources[0][0], resources[0][1]) - cheb(sx, sy, resources[0][0], resources[0][1])
    for rx, ry in resources[1:]:
        adv = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
        if adv > best_adv:
            best_adv = adv
            best_t = (rx, ry)

    tx, ty = best_t

    move_order = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    # Prefer immediate pickup (resource adjacent or same cell).
    res_set = set(resources)
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        capture = 1 if (nx, ny) in res_set else 0

        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)

        # Primary: advance our distance; also try to keep being closer than opponent on the target.
        score = -d_self
        score += 3 * capture
        score += 0.8 * (d_opp - d_self)

        # Secondary: avoid obstacles (smaller proximity is worse); mild nudge toward center-ish without randomness.
        score += 0.05 * obs_prox(nx, ny)
        score += -0.001 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_score > -10**8 else [0, 0]