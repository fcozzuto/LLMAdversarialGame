def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, tx, ty)
            if best is None or d < best_d:
                best = (dx, dy); best_d = d
        return [best[0], best[1]]

    # Pick a resource where we have the strongest "catch-up" potential
    best_target = None
    best_tkey = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer reachable advantage; then closeness; then deterministic ordering
        tkey = (od - sd, -sd, rx, ry)
        if best_tkey is None or tkey > best_tkey:
            best_tkey = tkey
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        # Encourage getting to the target while also discouraging letting opponent be closer
        # Tie-break by minimizing remaining distances and then deterministic deltas.
        key = (od2 - sd2, -sd2, -man(nx, ny, ox, oy), nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    # If we can step onto a resource immediately, do it deterministically
    for dx, dy in moves:
        if (sx + dx, sy + dy) in resources:
            return [dx, dy]

    return [best_move[0], best_move[1]]