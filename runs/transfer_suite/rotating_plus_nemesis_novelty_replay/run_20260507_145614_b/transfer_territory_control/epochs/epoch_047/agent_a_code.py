def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    self_cells = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_cells = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    targets = unclaimed if unclaimed else [p for p in (observation.get("opponent_territory") or [])]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a strategic target: far from opponent, not too far from us.
    tx, ty = sx, sy
    if targets:
        best_key = None
        for x, y in targets:
            if (x, y) in obstacles:
                continue
            du = man(sx, sy, x, y)
            do = man(observation["opponent_position"][0], observation["opponent_position"][1], x, y)
            # Prefer cells we can reach with a margin and that are also relatively close.
            k = (-(do - du), du, y, x)
            if best_key is None or k < best_key:
                best_key = k
                tx, ty = x, y

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]
    ox, oy = observation["opponent_position"]

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        # Immediate value: unclaimed and flipping opponent-owned.
        if (nx, ny) in opp_cells:
            base = 7.0
        elif (nx, ny) in unclaimed:
            base = 5.0
        elif (nx, ny) in self_cells:
            base = 1.0
        else:
            base = 0.6

        # Progress toward target, and keep some distance from opponent to avoid contested loss.
        d_t = man(nx, ny, tx, ty)
        d_o = man(nx, ny, ox, oy)
        score = base + (-0.15 * d_t) + (0.03 * d_o)

        # Tie-break deterministically.
        key = (-score, dy, dx)
        if best_score is None or key < best_key:
            best_score = score
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]