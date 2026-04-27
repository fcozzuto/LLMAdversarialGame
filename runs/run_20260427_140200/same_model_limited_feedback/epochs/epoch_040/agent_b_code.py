def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # Fallback: drift toward center while keeping away from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None; bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = -((nx - cx) ** 2 + (ny - cy) ** 2) + 0.5 * ((nx - ox) ** 2 + (ny - oy) ** 2)
                if v > bestv: bestv, best = v, (dx, dy)
        return list(best if best is not None else (0, 0))
    def d2(a, b): return (a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1])
    # Choose a target resource where we have a relative advantage
    best_t = None; best_adv = -10**18
    for rx, ry in resources:
        adv = d2((ox, oy), (rx, ry)) - d2((sx, sy), (rx, ry))  # larger means we are relatively closer
        if (sx, sy) == (rx, ry): adv += 10**9
        if adv > best_adv:
            best_adv, best_t = adv, (rx, ry)
    tx, ty = best_t
    best = (0, 0); bestv = -10**18
    # Move toward target while increasing distance from opponent; avoid obstacles and bounds
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): continue
        if (nx, ny) in obstacles: continue
        cur = d2((sx, sy), (tx, ty)); nxt = d2((nx, ny), (tx, ty))
        opp = d2((nx, ny), (ox, oy))
        # slight bias to reduce risk of being blocked by approaching along a corridor
        min_res = min(d2((nx, ny), r) for r in resources) if resources else 0
        v = -nxt + 0.35 * opp + 0.15 * (cur - nxt) - 0.02 * min_res
        if v > bestv:
            bestv, best = v, (dx, dy)
    return [int(best[0]), int(best[1])]