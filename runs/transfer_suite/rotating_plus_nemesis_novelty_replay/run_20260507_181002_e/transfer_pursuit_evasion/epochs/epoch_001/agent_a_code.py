def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    ox, oy = observation["opponent_position"]
    sx, sy = observation["self_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)
    is_evader = ("evader" in role) or (not is_pursuer)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    esc = max(corners, key=lambda c: max(abs(c[0] - ox), abs(c[1] - oy)))
    best = None
    best_key = None

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            dist = max(abs(nx - ox), abs(ny - oy))
            if is_evader:
                # maximize distance to opponent; then get closer to escape corner; then deterministic tie by coordinates
                d_corner = max(abs(nx - esc[0]), abs(ny - esc[1]))
                key = (dist, -d_corner, -nx, -ny)
            else:
                # minimize distance to opponent; then get closer to opponent's vicinity; then deterministic tie
                d_corner = max(abs(nx - ox), abs(ny - oy))
                key = (-d_corner, nx + ny, -nx, -ny)
            if best_key is None or key > best_key:
                best_key = key
                best = [dx, dy]
    if best is None:
        return [0, 0]
    return best