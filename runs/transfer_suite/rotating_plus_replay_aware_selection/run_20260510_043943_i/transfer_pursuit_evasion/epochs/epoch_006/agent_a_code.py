def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("chaser" in self_role) or ("hunter" in self_role)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    def step_from(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            return x, y
        return nx, ny

    def free_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    def score_opp_choice(mx, my):
        # opponent (evader) tries to maximize our distance after it moves; tie-break deterministically
        best = None
        for dx, dy in moves:
            nx, ny = step_from(ox, oy, dx, dy)
            d = dist2(mx, my, nx, ny)
            # tie-break: prefer moves with more mobility; then lexicographic (dx,dy)
            mob = free_count(nx, ny)
            key = (d, mob, -dx, -dy)  # deterministic ordering
            if best is None or key > best[0]:
                best = (key, (dx, dy, nx, ny))
        return best[1]

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = step_from(sx, sy, dx, dy)
        odx, ody, nox, noy = score_opp_choice(nx, ny)
        d_after = dist2(nx, ny, nox, noy)
        # If pursuer: minimize distance; else maximize
        # Tie-break: prefer higher free_count (avoid getting boxed), then stable move ordering
        mob = free_count(nx, ny)
        key = (-d_after if is_pursuer else d_after, mob, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]