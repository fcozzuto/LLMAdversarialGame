def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    turns_remaining = int(observation.get("turns_remaining") or 0)
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target with deterministic tie-breaking: first that we can plausibly beat, else best advantage.
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if sd > turns_remaining + 1:
            continue
        # Prefer: win-likely (sd <= od), then larger (od - sd), then smaller sd, then farther from opponent.
        winlike = 1 if sd <= od else 0
        key = (winlike, (od - sd), -sd, -od, rx, ry)
        if best_key is None or key > best_key:
            best_key, best_r = key, (rx, ry)

    if best_r is None:
        # If all were too far, just minimize our distance to the most 'reachable' resource.
        best_r, best_key = resources[0], None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obstacles:
                continue
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            key = (-(sd), (od - sd), rx, ry)
            if best_key is None or key > best_key:
                best_key, best_r = key, (rx, ry)

    tx, ty = int(best_r[0]), int(best_r[1])

    # Choose next step that improves our approach while not stepping into obstacles; also slightly discourages giving the opponent access.
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # If we can't beat on time, still move to maximize advantage; include small penalty for moving away from tx.
        key = (-my_d, (opp_d - my_d), abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    # Fallback if all candidate moves blocked.
    if best_move is None:
        return [0, 0]
    return best_move