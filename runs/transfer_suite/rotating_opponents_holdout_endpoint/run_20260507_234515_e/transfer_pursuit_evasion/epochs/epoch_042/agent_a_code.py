def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    self_is_pursuer = ("purs" in role) or (role == "")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in oset

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def corner_dist(x, y):
        return min(x + y, x + (h - 1 - y), (w - 1 - x) + y, (w - 1 - x) + (h - 1 - y))

    def wall_score(x, y):
        # Higher when closer to a wall/edge.
        return min(x, y, w - 1 - x, h - 1 - y)

    def free_neighbor_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best_move = (0, 0)
    best_val = None

    # Deterministic tie-breaking by move ordering.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = md(nx, ny, ox, oy)
        fnc = free_neighbor_count(nx, ny)

        if self_is_pursuer:
            # Minimize distance. Tie-break: prefer states that reduce opponent "escape space"
            # and push evader toward corners slightly.
            key = (d, -fnc, corner_dist(ox, oy))
            val = key
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # Evader: maximize distance, prefer hugging walls (wall runner),
            # and avoid reducing local mobility.
            ws = wall_score(nx, ny)  # smaller => closer to wall
            key = (-d, ws, -fnc)
            val = key
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]