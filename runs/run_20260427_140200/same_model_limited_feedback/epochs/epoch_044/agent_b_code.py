def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def dist(a,b,c,d):
        dx = a-c; dy = b-d
        return (dx*dx + dy*dy) ** 0.5
    def inb(x,y):
        return 0 <= x < w and 0 <= y < h
    # Select target resource: prefer ones we're closer to than opponent, otherwise closest to us.
    target = None
    best_margin = -10**9
    best_d = 10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        ds = dist(rx, ry, sx, sy)
        do = dist(rx, ry, ox, oy)
        margin = do - ds
        if margin > best_margin + 1e-9:
            best_margin = margin
            target = (rx, ry)
        if margin <= 1e-9 and ds < best_d:
            best_d = ds
    if target is None and resources:
        target = min(resources, key=lambda p: dist(p[0],p[1],sx,sy))
    # If no resources, move toward opponent to contest space.
    if target is None:
        target = (ox, oy)
    tx, ty = target
    # Evaluate candidate moves deterministically.
    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Heuristic: move to target, prefer also to cut off opponent (reduce their distance to target a bit).
        my_d = dist(nx, ny, tx, ty)
        opp_d = dist(nx, ny, ox, oy)
        opp_to_target = dist(ox, oy, tx, ty)
        # If we're behind opponent toward target, prioritize decreasing our distance more than their.
        if best_margin > 0:
            score = -my_d + 0.15 * opp_d
        else:
            score = -my_d + 0.08 * (opp_to_target - dist(ox, oy, tx, ty)) - 0.12 * opp_d
        # Tie-break: deterministic ordering favoring closer to opponent when equal.
        if score > best[0] + 1e-9 or (abs(score - best[0]) <= 1e-9 and (opp_d < best[1] or (opp_d == best[1] and (dx,dy) < (best[2],best[3])))):
            best = (score, opp_d, dx, dy)
    dx, dy = best[2], best[3]
    if dx is None or dy is None:
        return [0,0]
    return [int(dx), int(dy)]