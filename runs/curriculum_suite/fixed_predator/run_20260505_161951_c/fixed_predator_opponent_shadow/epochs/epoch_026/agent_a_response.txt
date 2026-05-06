def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Move to maximize distance from opponent
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = (abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Estimate what opponent is likely targeting (closest resource to opponent)
    opp_target = None
    opp_bestd = 10**18
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < opp_bestd:
            opp_bestd = d
            opp_target = (rx, ry)

    # If we can contest, go to it; otherwise pick a resource where we can reduce the gap most
    rx0, ry0 = opp_target
    self_to_opp_target = man(sx, sy, rx0, ry0)
    if self_to_opp_target <= opp_bestd:
        chosen = (rx0, ry0)
    else:
        chosen = resources[0]
        best_gain = -10**18
        best_selfd = 10**18
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            gain = (od - sd)  # bigger => we are more behind, but can aim to catch up to a less-problematic target
            # Flip preference: we want maximize (od - sd) when we are far behind, but also keep self distance reasonable
            key = gain * 10 - sd
            if key > best_gain:
                best_gain = key
                chosen = (rx, ry)
                best_selfd = sd

    tx, ty = chosen

    # One-step look: choose move that brings us closest to target, but if opponent is much closer there, try to deny by moving to a nearer alternative
    best = None
    best_score = 10**18
    for dx, dy, nx, ny in legal:
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer smaller self distance; discourage moves that don't improve enough against opponent's lead
        score = sd * 3 + max(0, sd - (od - 1)) + (abs(nx - ox) + abs(ny - oy)) * 0.05
        if score < best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]