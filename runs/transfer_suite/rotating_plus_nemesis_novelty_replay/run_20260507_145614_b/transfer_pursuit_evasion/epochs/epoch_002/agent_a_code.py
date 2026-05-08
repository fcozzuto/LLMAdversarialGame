def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obst = set((p[0], p[1]) for p in obstacles)
    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("pursuer" in self_role) or ("pursur" in self_role)

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def score_move(dx, dy, nx, ny):
        man = abs(nx - ox) + abs(ny - oy)
        # Obstacle proximity penalty/bonus (deterministic)
        near = 0
        for adx, ady in [(1,0),(-1,0),(0,1),(0,-1)]:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obst:
                near += 1
        # Bias toward staying on an "escape line" or "chase line"
        align = -abs((nx - sx) - (nx - ox)) - abs((ny - sy) - (ny - oy))
        # Tie-break deterministically by move ordering
        tie = (dx, dy)
        if is_pursuer:
            # capture if possible
            if nx == ox and ny == oy:
                return (-(10**9), 0, 0, tie)
            # minimize distance, avoid obstacle-adjacent squares slightly
            return (man, near, -align, tie)
        else:
            # avoid capture
            if nx == ox and ny == oy:
                return (10**9, 0, 0, tie)
            # maximize distance, reduce obstacle adjacency to avoid getting boxed
            return (-man, near, align, tie)

    best = None
    best_key = None
    for dx, dy, nx, ny in legal:
        k = score_move(dx, dy, nx, ny)
        if best_key is None or k < best_key:
            best_key = k
            best = (dx, dy)
    return [int(best[0]), int(best[1])]