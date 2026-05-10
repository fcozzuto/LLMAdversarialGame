def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                if 0 <= x < w and 0 <= y < h:
                    obstacles.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = observation.get("unclaimed_cells") or []
    if unclaimed:
        targets = [t for t in unclaimed if t and len(t) >= 2 and in_bounds(t[0], t[1])]
    else:
        targets = [t for t in (observation.get("resources") or []) if t and len(t) >= 2 and in_bounds(t[0], t[1])]
        if not targets:
            targets = [t for t in (observation.get("self_territory") or []) if t and len(t) >= 2 and in_bounds(t[0], t[1])]
    if not targets:
        return [0, 0]

    # Prefer cells that are closer to us and farther from the opponent.
    best = None
    best_key = None
    for x, y in targets:
        du = abs(x - sx) + abs(y - sy)
        do = abs(x - ox) + abs(y - oy)
        key = (du, -do, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If multiple moves improve equally, deterministic ordering of moves decides.
    cur_best_key = None
    cur_best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        du2 = abs(tx - nx) + abs(ty - ny)
        do2 = abs(ox - nx) + abs(oy - ny)

        # Small preference to avoid stepping into opponent proximity.
        # Also slightly prefer reducing distance to our target.
        key = (du2, -do2, abs(nx - tx) + abs(ny - ty), dx, dy)
        if cur_best_key is None or key < cur_best_key:
            cur_best_key = key
            cur_best = (dx, dy)

    dx, dy = cur_best
    return [int(dx), int(dy)]