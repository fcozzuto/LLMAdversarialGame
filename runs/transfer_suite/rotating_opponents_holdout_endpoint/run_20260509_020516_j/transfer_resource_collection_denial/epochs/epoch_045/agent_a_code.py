def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                moves.append((dx, dy, nx, ny))

    best = None
    best_score = -10**18
    best_sd = 10**18
    for dx, dy, nx, ny in moves:
        if (nx, ny) in obstacles:
            continue
        # Select best remaining resource for THIS move, using opponent-later advantage.
        local_best = -10**18
        local_sd = 10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > local_best or (adv == local_best and (sd < local_sd or (sd == local_sd and (rx, ry) < best))):
                local_best = adv
                local_sd = sd
        # Prefer larger advantage; if equal, prefer closer to some resource; then deterministic step order.
        step_order = (dx + 1) * 3 + (dy + 1)
        score = local_best * 10**6 - local_sd  # stable tie weighting
        if score > best_score or (score == best_score and (local_sd < best_sd or (local_sd == best_sd and step_order < (best[0] + 1) * 3 + (best[1] + 1) if best else True))):
            best_score = score
            best_sd = local_sd
            best = (dx, dy)

    if not best:
        return [0, 0]
    return [int(best[0]), int(best[1])]