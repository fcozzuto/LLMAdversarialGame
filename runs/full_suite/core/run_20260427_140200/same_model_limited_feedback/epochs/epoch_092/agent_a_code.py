def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (7, 7))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def clamp(x, y):
        if x < 0: x = 0
        if y < 0: y = 0
        if x >= w: x = w - 1
        if y >= h: y = h - 1
        return x, y
    def d2(a, b):
        dx = a[0]-b[0]; dy = a[1]-b[1]
        return dx*dx + dy*dy
    # Pick target resource where we have advantage (or nearest if none)
    best_r = None
    best_adv = -10**18
    nearest_r = None
    nearest_d = 10**18
    for r in resources:
        rx, ry = r[0], r[1]
        if d2((sx, sy), (rx, ry)) < nearest_d:
            nearest_d = d2((sx, sy), (rx, ry))
            nearest_r = (rx, ry)
        adv = d2((ox, oy), (rx, ry)) - d2((sx, sy), (rx, ry))
        if adv > best_adv:
            best_adv = adv
            best_r = (rx, ry)
    target = best_r if (resources and best_adv > 0) else nearest_r
    if target is None:
        target = (ox, oy)  # fallback
    tx, ty = target
    # Evaluate each move deterministically
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obst:
            continue
        # Base: get closer to target
        score = -d2((nx, ny), (tx, ty))
        # If target is contested, reduce opponent access: move to increase their distance
        opp_d = d2((ox, oy), (nx, ny))
        score += 0.35 * d2((ox, oy), (tx, ty)) - 0.35 * d2((nx, ny), (tx, ty))
        # Avoid getting too close to opponent unless we can "trade" by landing near target
        score += 0.25 * opp_d
        # Encourage stepping onto a resource tile
        if any((r[0], r[1]) == (nx, ny) for r in resources):
            score += 10000
        # Mild tie-break: prefer moves with smaller magnitude away from current direction to keep stable
        score += -0.01 * (abs(dx) + abs(dy))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]