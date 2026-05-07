def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    # If no visible resources, go to our nearest corner by Chebyshev distance to reduce time-to-visibility.
    if not resources:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        target = min(corners, key=lambda c: cheb((sx, sy), c) + 0.01 * cheb((ox, oy), c))
    else:
        # Choose a resource where we are relatively advantaged; break ties by closer distance to us.
        best = None
        for r in resources:
            rd = tuple(r)
            d1 = cheb((sx, sy), rd)
            d2 = cheb((ox, oy), rd)
            # Large weight favors securing resources opponent can't reach first.
            val = (d2 - d1, -d1, -(abs(rd[0] - sx) + abs(rd[1] - sy)))
            if best is None or val > best[0]:
                best = (val, rd)
        target = best[1]

    # Greedy move: reduce our distance to target, but also keep away from opponent to avoid contested collection.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        our_next = cheb((nx, ny), target)
        opp_next = cheb((nx, ny), (ox, oy))
        d_our = cheb((sx, sy), target)
        d_opp = cheb((sx, sy), (ox, oy))
        score = (d_our - our_next, our_next * -1, (opp_next - d_opp), opp_next)
        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]