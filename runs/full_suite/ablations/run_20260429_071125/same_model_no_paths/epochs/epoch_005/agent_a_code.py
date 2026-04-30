def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def score_cell(nx, ny):
        if (nx, ny) in blocked:
            return -10**18
        center = cheb(nx, ny, cx, cy)
        if not resources:
            return -center
        best = -10**18
        best_our_d = 10**18
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d  # positive => we are closer
            # Prefer winning a resource soon; add small center preference to break ties deterministically.
            s = adv * 1000 - our_d - center
            if s > best or (s == best and (our_d < best_our_d)):
                best = s
                best_our_d = our_d
        return best

    best_move = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue
        s = score_cell(nx, ny)
        if s > best_s:
            best_s = s
            best_move = (dx, dy)
        elif s == best_s:
            # Deterministic tie-break: prefer smaller Chebyshev step toward center, then toward resources.
            if cheb(nx, ny, cx, cy) < cheb(sx + best_move[0], sy + best_move[1], cx, cy):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]