def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        cx, cy = (gw - 1) / 2.0, (gh - 1) / 2.0
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in cand:
            v = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) - 0.05 * (abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in cand:
        # Evaluate the best resource we could realistically contest after this move
        move_score = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer than opponent
            # Encourage winning contests, but also prefer nearer resources when contests are tied
            # Additional term: if we can reach very quickly, it beats lingering
            urgency = 1.0 / (1 + sd)
            # If opponent is extremely close, being closer matters more
            pressure = 0.5 if od <= sd + 1 else 0.0
            v = 6.0 * adv + 2.0 * urgency + pressure - 0.1 * sd
            if v > move_score:
                move_score = v
        # Small tie-breaker: discourage moves that put us behind across all resources
        # (keeps behavior stable vs shadow chasing).
        min_behind = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            min_behind = min(min_behind, sd - od)
        total = move_score - 0.2 * max(0, min_behind)
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]