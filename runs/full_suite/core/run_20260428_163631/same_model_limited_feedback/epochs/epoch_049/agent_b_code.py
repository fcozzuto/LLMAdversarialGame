def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        return (dx*dx + dy*dy)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    best_r = None
    best_adv = None
    for r in resources:
        rx, ry = r
        d_s = dist((sx, sy), (rx, ry))
        d_o = dist((ox, oy), (rx, ry))
        adv = d_o - d_s
        if best_r is None or adv > best_adv or (adv == best_adv and d_s < dist((sx, sy), best_r)):
            best_r = r; best_adv = adv
    tx, ty = best_r if best_r is not None else (sx, sy)
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = dist((nx, ny), (tx, ty))
        d_op = dist((nx, ny), (ox, oy))
        # prefer moving to a resource where we are ahead; also avoid letting opponent collapse onto it
        target_risk = 0
        for r in resources:
            rx, ry = r
            target_risk += max(0, dist((ox, oy), (rx, ry)) - dist((nx, ny), (rx, ry))) * 0
        score = d_op * 0.05 + d_to
        scored.append((score, -d_op, dx, dy))
    if not scored:
        return [0, 0]
    scored.sort()
    return [int(scored[0][2]), int(scored[0][3])]