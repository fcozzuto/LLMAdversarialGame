def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    moves = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x, y):
        # Chebyshev is good for diagonal pursuit/escape
        return max(abs(x - ox), abs(y - oy))

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    best = None
    best_key = None

    # For evader: head to the farthest corner from pursuer (deterministic)
    if evader:
        far_corner = None
        for cx, cy in [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]:
            d = max(abs(cx - ox), abs(cy - oy))
            if far_corner is None or d > far_corner[0]:
                far_corner = (d, cx, cy)
        tx, ty = far_corner[1], far_corner[2]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist(nx, ny)
        mob = mobility(nx, ny)

        if evader:
            # maximize distance from pursuer; also move toward target corner
            corner_bonus = - (abs(nx - tx) + abs(ny - ty))
            key = (d, corner_bonus, mob, -abs(nx - sx) - abs(ny - sy), dx, dy)
            # choose max key lexicographically
            if best is None or key > best_key:
                best, best_key = (dx, dy), key
        else:
            # minimize distance from pursuer; tie-break for mobility and central tendency
            center = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
            key = (-d, mob, center, -abs(nx - ox) - abs(ny - oy), dx, dy)
            if best is None or key > best_key:
                best, best_key = (dx, dy), key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]