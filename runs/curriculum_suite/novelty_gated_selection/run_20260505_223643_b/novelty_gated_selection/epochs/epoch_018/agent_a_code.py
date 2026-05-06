def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick target resource with maximum "advantage" (opponent farther than us).
    best = None
    tx, ty = sx, sy
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # Prefer larger advantage, then smaller own distance, then closer to center.
        center_bias = -abs((w - 1) / 2 - rx) - abs((h - 1) / 2 - ry)
        key = (adv, -sd, center_bias, -(rx + ry))
        if best is None or key > best:
            best = key
            tx, ty = rx, ry

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate immediate moves; reject ones landing on obstacles/out of bounds.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd

        # Small deterrent if we are not improving toward the chosen target.
        improve = -sd

        # If opponent is very near the target, bias to resources closer to us than them.
        # Use a quick check for top alternative resource.
        alt_adv = -10**9
        for rx, ry in resources:
            a_sd = cheb(nx, ny, rx, ry)
            a_od = cheb(ox, oy, rx, ry)
            a = a_od - a_sd
            if a > alt_adv:
                alt_adv = a
        score = (adv, alt_adv, improve)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # Fallback: if all legal moves blocked, stay.
    return [int(best_move[0]), int(best_move[1])]