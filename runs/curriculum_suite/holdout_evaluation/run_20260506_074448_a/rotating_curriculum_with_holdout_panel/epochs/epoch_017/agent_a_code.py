def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def interior_bias(x, y):
        d = x
        if w - 1 - x < d:
            d = w - 1 - x
        if y < d:
            d = y
        if h - 1 - y < d:
            d = h - 1 - y
        return -d  # closer to center (larger d) => less negative

    best_dx, best_dy = 0, 0
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        base = interior_bias(nx, ny)
        best_for_move = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_me  # positive means we can be no later than opponent in Cheb moves
            # Strongly prioritize winning a contest; otherwise prefer approaching nearest contestable resource
            score = (20 * adv + 3) if adv >= 0 else (4 * adv)
            score += -d_me + base * 0.2
            if score > best_for_move:
                best_for_move = score
        if best_for_move > best_score:
            best_score = best_for_move
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]