def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w // 2, h // 2)
        tx = 0 if cx == sx else (1 if cx > sx else -1)
        ty = 0 if cy == sy else (1 if cy > sy else -1)
        return [tx, ty]

    # Evaluate each candidate move by how well it wins races to resources.
    best_score = -10**30
    best_move = [0, 0]
    tie = 0
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if blocked(nx, ny):
            nx, ny = sx, sy  # engine keeps in place
        s_best = -10**30
        o_best = 10**30

        for rx, ry in resources:
            sd = dist8(nx, ny, rx, ry)
            od = dist8(ox, oy, rx, ry)
            # Race win margin: larger is better. Small preference for immediate pickup.
            margin = od - sd
            val = margin * 1000 - sd
            if sd == 0:
                val += 10**9
            if val > s_best:
                s_best = val
                o_best = od

        # Deny bonus: prefer moves that increase opponent's distance to the resource we'd target.
        # (Approx via best resource currently chosen by self after the move.)
        # Also add slight bias toward staying on the same parity to reduce oscillations.
        parity_bias = -((nx + ny) & 1) * 0.001
        score = s_best + (o_best * -0.0001) + parity_bias

        # Deterministic tie-breaker: lower index move wins.
        if score > best_score or (score == best_score and tie < best_move[2]):
            best_score = score
            best_move = [dxm, dym, tie]
        tie += 1

    return [best_move[0], best_move[1]]