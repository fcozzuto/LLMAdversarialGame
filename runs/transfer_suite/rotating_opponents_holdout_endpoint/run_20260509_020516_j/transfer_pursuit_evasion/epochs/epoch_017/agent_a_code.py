def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best_move = (0, 0)
    if pursuer:
        # Chasing with local "escape potential" to avoid stepping into corners/dead-ends.
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            fn = free_neighbors(nx, ny)
            # Prefer smaller distance; if tie, prefer higher mobility.
            key = (-d, fn, -abs(ox - nx) - abs(oy - ny))
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
    else:
        # Evader: maximize distance, but bias toward keeping options (avoid being trapped by obstacles).
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            fn = free_neighbors(nx, ny)
            # Prefer larger distance; then larger mobility; then prefer moving away in both axes.
            key = (d, fn, (nx - ox) * (sx - ox), (ny - oy) * (sy - oy))
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]