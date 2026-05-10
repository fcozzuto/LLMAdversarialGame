def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)
    role = (observation.get("self_role") or "pursuer").lower()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def manh(x, y): return abs(x - ox) + abs(y - oy)
    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    # deterministic step evaluation
    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        m = manh(nx, ny)

        # Key differs by role: pursuer minimizes distance; evader maximizes distance
        if role == "pursuer":
            # also prefer moves that can keep maneuvering and avoid being cornered
            key = (m, -mobility(nx, ny), 0 if dx == 0 else (1 if dx > 0 else -1), 0 if dy == 0 else (1 if dy > 0 else -1))
        else:
            # evader: maximize distance; then maximize mobility; then prefer staying off direct-line toward pursuer
            next_m = manh(nx, ny)
            step_toward = (1 if nx != ox else 0) + (1 if ny != oy else 0)
            key = (-next_m, -mobility(nx, ny), step_toward, 0 if dx == 0 else (1 if dx > 0 else -1), 0 if dy == 0 else (1 if dy > 0 else -1))

        if best is None or key < best_key:
            best = (dx, dy)
            best_key = key

    if best is None:
        return [0, 0]
    return [best[0], best[1]]