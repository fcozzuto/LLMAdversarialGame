def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cenx, ceny = (w - 1) / 2.0, (h - 1) / 2.0

    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        s_new = nx, ny
        best_for_move = -10**18
        for tx, ty in resources:
            sdist = cheb(s_new[0], s_new[1], tx, ty)
            odist = cheb(ox, oy, tx, ty)

            # Opponent can also move this turn; estimate one-step closer.
            od_est = odist - 1
            lead = od_est - sdist  # positive means we are more likely to grab it first

            center_bias = -0.02 * (abs(tx - cenx) + abs(ty - ceny))
            # Avoid moving toward resources opponent is already closer to (low lead).
            penalty = -0.3 * (lead < 0)
            sc = 3.0 * lead - 0.15 * sdist + center_bias + penalty
            if sc > best_for_move:
                best_for_move = sc

        # Prefer taking if we are exactly on a resource.
        if (nx, ny) in resources:
            best_for_move += 10.0
        if best_for_move > best[1]:
            best = ((dx, dy), best_for_move)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]