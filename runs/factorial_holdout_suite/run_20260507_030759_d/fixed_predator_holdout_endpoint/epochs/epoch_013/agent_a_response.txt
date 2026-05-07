def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        # Move toward center deterministically
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = max(abs(tx - nx), abs(ty - ny))
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    def cheb(ax, ay, bx, by):
        return abs(ax - bx) if abs(ax - bx) > abs(ay - by) else abs(ay - by)

    # New policy: maximize our immediate advantage over opponent for the same resource; if none, minimize opponent advantage.
    best_move = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_adv = None
        best_resource_dist = None
        opp_best = None
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self  # positive => we are closer than opponent
            if best_adv is None or adv > best_adv or (adv == best_adv and d_self < best_resource_dist):
                best_adv = adv
                best_resource_dist = d_self
            # Track best opponent threat (smallest opp distance to any remaining resource)
            d_opp2 = d_opp
            if opp_best is None or d_opp2 < opp_best:
                opp_best = d_opp2
        # Prefer securing: higher best_adv, then closer resource, then avoid being in a losing position.
        # Add small tie-break toward moving "down/right" by using dx,dy order.
        key = (-best_adv, best_resource_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]