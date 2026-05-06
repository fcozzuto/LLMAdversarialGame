def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy = 0, 0
    best_key = None

    # Denial-oriented: maximize (opponent's nearest-resource distance - our nearest-resource distance)
    # i.e., keep opponent far from resources while keeping us relatively close.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        our_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            d1 = manh(nx, ny, rx, ry)
            if d1 < our_best:
                our_best = d1
            d2 = manh(ox, oy, rx, ry)
            if d2 < opp_best:
                opp_best = d2
        # Small extra bias: if we can land closer to the opponent currently, it's good for interception.
        inter = manh(nx, ny, ox, oy)
        key = (opp_best - our_best, -our_best, -inter, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]