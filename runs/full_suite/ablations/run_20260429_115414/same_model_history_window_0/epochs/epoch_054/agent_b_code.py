def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    if not resources:
        # If no visible resources, move to reduce distance from opponent only if far; otherwise hold.
        best = (10**9, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            d = abs(nx - ox) + abs(ny - oy)
            sc = d if (observation.get("turn_index", 0) % 2 == 0) else -d
            if sc < best[0]:
                best = (sc, (dx, dy))
        return [best[1][0], best[1][1]]
    t = observation.get("turn_index", 0)
    best_target = None
    best_val = None
    for rx, ry in resources:
        ds = abs(sx - rx) + abs(sy - ry)
        do = abs(ox - rx) + abs(oy - ry)
        # Alternate strategy: even turns push for resources we're closer to; odd turns avoid opponent by taking "safer" ones.
        if t % 2 == 0:
            val = ds - 0.35 * do
        else:
            # Prefer resources far from opponent, but still reachable
            val = 0.5 * ds - 0.9 * do
        if best_val is None or val < best_val:
            best_val = val
            best_target = (rx, ry)
    rx, ry = best_target
    # Choose a legal move that decreases distance to target, avoids obstacles, and keeps some distance from opponent.
    best = (10**18, (0, 0))
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = abs(nx - rx) + abs(ny - ry)
        do2 = abs(nx - ox) + abs(ny - oy)
        # Penalties: being adjacent to opponent, or moving away from target
        penalty_close = 0
        if do2 <= 1: penalty_close = 25 if t % 2 == 0 else 40
        penalty_move = 0 if (dx == 0 and dy == 0) else 0
        # Encourage progress; slight tie-breaker to keep heading direction stable
        sc = ds2 + penalty_close + penalty_move + (0.001 * (dx*dx + dy*dy)) + (0.01 * do2)
        if sc < best[0]:
            best = (sc, (dx, dy))
    return [best[1][0], best[1][1]]