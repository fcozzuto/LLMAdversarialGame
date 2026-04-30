def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy)]
    if not dirs:
        return [0, 0]
    center = (w // 2, h // 2)
    # Pick a primary target deterministically: max of (opp closer advantage) then tie by near center
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        dm = cheb((sx, sy), (rx, ry))
        do = cheb((ox, oy), (rx, ry))
        key = (do - dm, -dm, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    if best_r is None:
        best_r = center
    tx, ty = best_r
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        myd = cheb((nx, ny), (tx, ty))
        myd0 = cheb((sx, sy), (tx, ty))
        # Advantage: how much closer we get vs opponent for the best contested resource
        max_adv = -10**9
        min_our = 10**9
        for r in resources:
            rx, ry = r
            if (rx, ry) in obstacles:
                continue
            dm = cheb((nx, ny), (rx, ry))
            do = cheb((ox, oy), (rx, ry))
            adv = do - dm
            if adv > max_adv:
                max_adv = adv
            if dm < min_our:
                min_our = dm
        # If no resources, just head to target/center
        if not resources:
            max_adv = -cheb((nx, ny), center)
            min_our = myd
        # Tie-breakers: prefer reducing distance to target, avoid getting farther from center, deterministic lexicographic
        cx = center[0] - nx
        if cx < 0: cx = -cx
        cy = center[1] - ny
        if cy < 0: cy = -cy
        cdist = cx if cx > cy else cy
        val = (max_adv, -(myd), -(min_our), -(cdist), -dx, -dy)  # lexicographic deterministic
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]