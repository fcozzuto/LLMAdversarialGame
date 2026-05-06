def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def edge_dist(x, y):
        a = x if x < w - 1 - x else w - 1 - x
        b = y if y < h - 1 - y else h - 1 - y
        return a if a < b else b

    # If no resources, drift to safer interior while avoiding opponent.
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = edge_dist(nx, ny) + 0.02 * cheb(nx, ny, ox, oy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Greedy resource targeting with opponent-pressure penalty.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_min = 10**9
        opp_min = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            if d1 < my_min: my_min = d1
            d2 = cheb(ox, oy, rx, ry)
            if d2 < opp_min: opp_min = d2
        # Prefer reducing distance to closest resource, but strongly avoid becoming the "slower" collector.
        score = -my_min + 0.03 * edge_dist(nx, ny)
        score -= 1.2 * max(0, my_min - opp_min)  # if opponent is closer, penalize
        # Extra: discourage stepping into/adjacent to opponent.
        score -= 0.25 * cheb(nx, ny, ox, oy)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]] if best else [0, 0]