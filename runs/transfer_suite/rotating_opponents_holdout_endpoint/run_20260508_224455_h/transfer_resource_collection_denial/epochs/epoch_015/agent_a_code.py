def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if (sx, sy) in obstacles:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx + dy

    sp = (sx + sy) & 1
    op = (ox + oy) & 1

    # Targeting change: prefer resources where we are closer than opponent, but also favor parity mismatch to disrupt sweep behavior.
    best = None
    for rx, ry in resources:
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        parity_bonus = 1 if (((rx + ry) & 1) != op) else 0
        # Primary: maximize advantage (od - sd). Secondary: closer to we can grab soon. Tertiary: parity/coordinate.
        key = (od - sd, -sd, -od, parity_bonus, -(rx + ry), -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    # Step choice: avoid obstacles, move to reduce our distance; when tied, prefer moves that increase opponent distance to target.
    best_step = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in resources:
            return [dx, dy]
        nsd = man((nx, ny), (tx, ty))
        nod = man((ox, oy), (tx, ty))
        # opponent constant; instead use how much we "commit" to target vs. give opponent closer access indirectly via our parity flip
        npar = (nx + ny) & 1
        commit = -nsd
        opp_impact = (man((ox, oy), (nx, ny)) - man((ox, oy), (sx, sy)))  # larger means we're moving away from opponent
        key = (commit, opp_impact, 1 if npar != op else 0, -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_step = [dx, dy]

    return best_step