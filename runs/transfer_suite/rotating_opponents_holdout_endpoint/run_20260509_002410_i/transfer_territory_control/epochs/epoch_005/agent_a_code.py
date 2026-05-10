def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Go to "our" corner while staying away from a sweeper.
    my_corner = (0, 0) if man(sx, sy, 0, 0) <= man(sx, sy, w - 1, h - 1) else (w - 1, h - 1)

    best_move = (0, 0)
    best_val = -10**18

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Pre-pick a deterministic target among unclaimed:
    if not unclaimed:
        target = (my_corner[0] + (w - 1 - my_corner[0]) // 2, my_corner[1] + (h - 1 - my_corner[1]) // 2)
    else:
        # Choose cell that is both good for expansion and bad for opponent proximity.
        target = unclaimed[0]
        best_t = -10**18
        for tx, ty in unclaimed:
            if not inside(tx, ty):
                continue
            v = (man(ox, oy, tx, ty) * 2) - man(sx, sy, tx, ty) - man(tx, ty, my_corner[0], my_corner[1])
            # Slightly prefer stealing if it doesn't make us vulnerable
            if (tx, ty) in opp_t:
                v += 6
            if v > best_t:
                best_t = v
                target = (tx, ty)

    tx, ty = target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Safety: don't run into opponent; prefer reducing distance to target.
        val = 0
        val += (man(ox, oy, nx, ny) - man(ox, oy, sx, sy)) * 3
        val += (man(sx, sy, tx, ty) - man(nx, ny, tx, ty)) * 4
        # Encourage moving toward our corner to avoid getting herded.
        val += (man(sx, sy, my_corner[0], my_corner[1]) - man(nx, ny, my_corner[0], my_corner[1])) * 1
        # If stepping onto opponent territory, only do it when it also improves safety.
        if (nx, ny) in opp_t:
            val += 8 if man(ox, oy, nx, ny) >= man(ox, oy, sx, sy) else 2
        # Deterministic tie-break: smallest dx, then dy
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]