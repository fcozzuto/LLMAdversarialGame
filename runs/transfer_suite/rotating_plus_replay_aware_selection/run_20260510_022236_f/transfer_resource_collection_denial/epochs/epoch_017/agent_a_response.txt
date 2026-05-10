def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set((int(x), int(y)) for x, y in obstacles)

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

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    # Pick target: maximize how much closer we are than opponent (in Chebyshev)
    best = None  # (lead, -self_d, opp_d, x, y)
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        lead = opp_d - self_d
        cand = (lead, -self_d, opp_d, int(rx), int(ry))
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    tx, ty = best[3], best[4]
    # Candidate moves with obstacle avoidance and tie-breaks
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    my_d0 = cheb(sx, sy, tx, ty)
    opp_d0 = cheb(ox, oy, tx, ty)

    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        self_d = cheb(nx, ny, tx, ty)
        opp_d = opp_d0  # opponent stays this turn; we only care about relative progress
        gain = my_d0 - self_d
        # Prefer big progress; then keep lead advantage for eventual capture
        rel = opp_d - self_d
        # Deterministic tie-break order: higher rel, higher gain, then closer among equal, then lexicographic move
        score = (rel, gain, -self_d, -dx, -dy)
        if bestm is None or score > bestm[0]:
            bestm = (score, dx, dy)

    if bestm is not None:
        return [int(bestm[1]), int(bestm[2])]

    # If all blocked (should be rare), try to stay (engine keeps position on invalid)
    return [0, 0]