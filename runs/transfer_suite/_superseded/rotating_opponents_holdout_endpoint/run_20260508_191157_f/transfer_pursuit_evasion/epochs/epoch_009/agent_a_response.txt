def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)
    role = observation.get("self_role", "pursuer").lower()
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

    # choose candidate corner maximizing distance from pursuer
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = corners[0]
    best_corner_d = -1
    for cx, cy in corners:
        d = md(cx, cy, ox, oy)
        if d > best_corner_d:
            best_corner_d, best_corner = d, (cx, cy)

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) == (ox, oy) and role == "pursuer":
            return [dx, dy]
        if role == "pursuer":
            d = md(nx, ny, ox, oy)
            key = (d, -mobility(nx, ny), nx, ny)
        else:
            d_opp = md(nx, ny, ox, oy)
            d_corner = md(nx, ny, best_corner[0], best_corner[1])
            # maximize distance from opponent; prefer moving toward the chosen corner; tie-break with mobility
            key = (-d_opp, d_corner, -mobility(nx, ny), nx, ny)
        if best_key is None or key < best_key:
            best_key, best_move = key, [dx, dy]
    return [best_move[0], best_move[1]]