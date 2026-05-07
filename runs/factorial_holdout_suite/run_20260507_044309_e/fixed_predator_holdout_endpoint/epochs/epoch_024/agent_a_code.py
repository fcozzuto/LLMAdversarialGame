def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_score(x, y):
        # Advantage: we want lead in distance; also prefer being close to a collectible.
        # Heavy penalty for obstacles; mild penalty for moving away from the best target.
        best = -10**18
        for rx, ry in resources:
            sd = man(x, y, rx, ry)
            od = man(ox, oy, rx, ry)
            lead = od - sd  # positive if we are closer than opponent (for that resource)
            v = 30 * lead - sd
            if v > best:
                best = v
        return best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            penalty = 0
            if (nx, ny) in obstacles:
                penalty = 10**9
            score = cell_score(nx, ny) - penalty
            # Tie-break deterministically: prefer smaller dx, then smaller dy, then staying
            moves.append((score, dx, dy))

    moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = moves[0]
    return [int(dx), int(dy)]