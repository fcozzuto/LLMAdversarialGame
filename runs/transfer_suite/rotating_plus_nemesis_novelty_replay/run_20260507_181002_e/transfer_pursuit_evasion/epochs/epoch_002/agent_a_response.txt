def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)
    is_evader = ("evader" in role) or (not is_pursuer)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def mobility(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                    c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    esc_corner = max(corners, key=lambda c: max(abs(c[0] - ox), abs(c[1] - oy)))
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = max(abs(nx - ox), abs(ny - oy))
            mob = mobility(nx, ny)
            d_corner = max(abs(nx - esc_corner[0]), abs(ny - esc_corner[1]))
            # Deterministic tie-breakers by position
            if is_evader:
                key = (d, mob, -d_corner, -nx, -ny)
            else:
                # pursuer: close in; then prefer higher mobility to keep options
                key = (-d, mob, -abs(nx - ox) - abs(ny - oy), nx, ny)
            candidates.append((key, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0], reverse=True)
    return [candidates[0][1], candidates[0][2]]