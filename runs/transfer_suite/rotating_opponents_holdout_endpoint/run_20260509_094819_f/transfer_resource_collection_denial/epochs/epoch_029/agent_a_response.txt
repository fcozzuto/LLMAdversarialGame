def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    resources = sorted(set(resources))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates = [(dx, dy) for dx, dy in dirs if not (dx == 0 and dy == 0)] + [(0, 0)]

    def cheb(ax, ay, bx, by):
        a = ax - bx
        if a < 0: a = -a
        b = ay - by
        if b < 0: b = -b
        return a if a > b else b

    # Choose move by evaluating best target under a "deny/advance" heuristic with obstacle-safe stepping.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            nx, ny = sx, sy  # invalid move is effectively staying in place

        move_score = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Higher is better: we want to be closer than opponent and also move toward a resource soon.
            s = (od - sd) * 100 - sd
            if s > move_score:
                move_score = s

        # Small tie-break: prefer moves that also reduce our distance to the globally best target.
        # Deterministic tie-break by lexicographic move order already via iteration order.
        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]