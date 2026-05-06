def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    res = [(int(p[0]), int(p[1])) for p in resources]
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Deterministic weights to compete vs a row-sweeping opponent: focus on fast resource access
    # and avoid moving into positions where opponent can grab resources sooner.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate this candidate by comparing our closest resource vs opponent's closest resource.
        dmin_self = 10**9
        dmin_opp = 10**9
        nearest = None
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            if ds < dmin_self:
                dmin_self = ds
                nearest = (rx, ry)
            do = cheb(ox, oy, rx, ry)
            if do < dmin_opp:
                dmin_opp = do

        # Encourage being strictly faster than opponent for the most relevant target.
        # Also include a small tie-break to prefer reducing our distance.
        lead = dmin_opp - dmin_self  # higher is better
        # Small penalty for moving "toward" opponent in chebyshev space to reduce collision/steal risk.
        risk = cheb(nx, ny, ox, oy)

        # Additional structure: if opponent is aligned in x with many resources, reduce alignment moves (row-sweep defense).
        align_bonus = 0
        if nearest is not None and (nearest[0] == ox or nearest[0] == sx):
            align_bonus = 2

        val = (lead * 30) - (dmin_self * 3) - (risk * 1.5) + align_bonus
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]