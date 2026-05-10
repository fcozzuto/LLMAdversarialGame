def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)
    role = observation.get("self_role", "pursuer")
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def md(x, y, a, b): return abs(x - a) + abs(y - b)

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    best_move = [0, 0]
    if role == "pursuer":
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs:
                continue
            if (nx, ny) == (ox, oy):
                return [dx, dy]
            d = md(nx, ny, ox, oy)
            key = (d, -mobility(nx, ny), nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    # Evader
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) == (ox, oy):
            continue
        d = md(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        # Prefer larger distance; avoid low-mobility moves; also slightly bias away from walls via bounds slack.
        slack = min(nx, ny, w - 1 - nx, h - 1 - ny)
        key = (-d, mob, -slack, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move