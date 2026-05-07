def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    obstacles = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources", []) or []
    resources = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]

    resset = set(resources)
    if (sx, sy) in resset:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Score moves by how much closer we are than the opponent to the best contested resource.
    # Tie-break deterministically by (my_best_dist, dx, dy).
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_best_gap = -10**9
        my_best_dist = 10**9
        for rx, ry in resources:
            md = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            gap = od - md  # positive means we're closer
            if gap > my_best_gap or (gap == my_best_gap and md < my_best_dist):
                my_best_gap = gap
                my_best_dist = md
        # Encourage immediate collection and prefer smaller distances when gaps tie.
        key = (my_best_gap, -my_best_dist, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]