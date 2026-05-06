def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Prefer taking resources where we are closer than opponent; otherwise drift away from opponent.
    if resources:
        dcur = man(sx, sy, ox, oy)
        # Score each resource by how much tempo we have, plus a small preference for nearer resources.
        best_res = None
        best_key = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            tempo = do - ds  # positive means we can arrive earlier (or tie with advantage)
            # If tempo is similar, prefer closer and also slightly prefer resources nearer to our side.
            key = (tempo, -ds, -abs((rx - (w - 1) / 2)) - abs((ry - (h - 1) / 2)))
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)

        rx, ry = best_res
        # If we have no real tempo advantage, still go to a resource but bias to avoid opponent pressure.
        focus = best_key[0] >= 1

        best_move = None
        best_mv_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            ds_next = man(nx, ny, rx, ry)
            do_next = man(nx, ny, ox, oy)
            # Tie-breakers are deterministic via tuple ordering.
            # If focus: maximize (opponent reach - our reach). Else: maximize distance from opponent while not going crazy.
            if focus:
                tempo_next = man(ox, oy, rx, ry) - ds_next
                key = (tempo_next, -ds_next, -man(nx, ny, ox, oy), nx, ny)
            else:
                key = (man(nx, ny, ox, oy) - dcur, -ds_next, -man(nx, ny, rx, ry), nx, ny)
            if best_mv_key is None or key > best_mv_key:
                best_mv_key = key
                best_move = (dx, dy)

        return [best_move[0], best_move[1]] if best_move is not None else [0, 0]

    # No resources: flee opponent while moving toward center (deterministic).
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = (man(nx, ny, ox, oy) * 3) - (man(nx, ny, cx, cy) * 1)
        if bestv is None or v > bestv or (v == bestv and (nx, ny) < best_move):
            bestv = v
            best_move = (nx, ny)
    if best_move is None:
        return [0, 0]
    return [best_move[0] - sx, best_move[1] - sy]