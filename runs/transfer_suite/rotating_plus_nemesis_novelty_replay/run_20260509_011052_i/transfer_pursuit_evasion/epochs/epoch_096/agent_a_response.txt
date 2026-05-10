def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    role = (observation.get("self_role") or "").lower()
    pursue = role != "evader"

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = 0, 0
    bestc = 10**18
    for cx, cy in corners:
        d = cheb(ox, oy, cx, cy)
        if d < bestc:
            bestc, tx, ty = d, cx, cy

    sgn = lambda v: 0 if v == 0 else (1 if v > 0 else -1)
    ddx = sgn(tx - ox)
    ddy = sgn(ty - oy)

    # Trapping target: one step in the direction that would keep opponent pressed into the corner.
    trapx = ox + ddx
    trapy = oy + ddy
    if not inb(trapx, trapy):
        trapx, trapy = tx, ty

    # If opponent already very close to the corner, prioritize trap positioning over direct chase.
    near_corner = cheb(ox, oy, tx, ty) <= 2

    best_move = (0, 0)
    best_score = -10**18 if pursue else 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_trap = cheb(nx, ny, trapx, trapy)

        # Additional "block" bias: move that reduces the chebyshev distance between self and
        # the line-of-corner direction from opponent.
        block_bias = 0
        if near_corner:
            # Prefer matching direction from opponent toward corner.
            # Score rises when self is aligned closer to the corner-boundary direction.
            block_bias = -((nx - (ox + ddx)) ** 2 + (ny - (oy + ddy)) ** 2)

        if pursue:
            score = (-d_opp if not near_corner else -2 * d_opp) + (-d_trap if near_corner else -0.5 * d_trap) + 0.001 * block_bias
            if score > best_score:
                best_score, best_move = score, (dx, dy)
        else:
            score = (d_opp if not near_corner else 2 * d_opp) + (d_trap if near_corner else 0.5 * d_trap) - 0.001 * block_bias
            if score < best_score:
                best_score, best_move = score, (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]