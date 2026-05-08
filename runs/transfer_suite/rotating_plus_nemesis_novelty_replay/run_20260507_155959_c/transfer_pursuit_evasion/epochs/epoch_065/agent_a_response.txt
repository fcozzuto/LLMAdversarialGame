def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def min_dist_to_obstacles(x, y):
        md = 99
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role)

    if is_evader:
        # Pick the corner that maximizes distance from pursuer, then move toward it while staying far.
        tx, ty = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), -abs(c[0] - sx) - abs(c[1] - sy)))
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = abs(nx - ox) + abs(ny - oy)
            d_corner = abs(nx - tx) + abs(ny - ty)
            clear = min_dist_to_obstacles(nx, ny)
            key = (d_opp, -d_corner, clear, -abs(dx) - abs(dy))
            if best_key is None or key > best_key:
                best_key, best = key, [dx, dy]
        return best if best is not None else [0, 0]

    # Pursuer: chase opponent, but bias toward the corner evader seems heading for.
    # Estimate evader target corner as the corner closest to opponent.
    tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_corner = abs(nx - tx) + abs(ny - ty)
        clear = min_dist_to_obstacles(nx, ny)
        # Primary: minimize capture-distance; secondary: improve clearance; tertiary: reduce corner distance.
        key = (-d_opp, clear, -d_corner, -(abs(dx) + abs(dy)))
        if best_key is None or key > best_key:
            best_key, best = key, [dx, dy]
    return best if best is not None else [0, 0]