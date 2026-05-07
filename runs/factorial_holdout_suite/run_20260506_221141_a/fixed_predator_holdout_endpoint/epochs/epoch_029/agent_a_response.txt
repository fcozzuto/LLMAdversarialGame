def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def clamp_inbounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Filter legal moves (stay if blocked/outside)
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if clamp_inbounds(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Evaluate move by best resource preference after the move
    # Prefer resources where we are closer than opponent; if none, pick one with smallest self distance.
    best_move = (0, 0)
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_resource_val = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obs:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Denier-aware: maximize margin against opponent, then minimize our distance
            # Strongly encourage winning the race to a resource (larger positive margin).
            margin = od - sd
            val = (10 * margin) - sd
            # If we're not closer, reduce value more (resource competition)
            if margin <= 0:
                val -= 20 + sd
            # Tie-break deterministically by coordinates
            tie = (-rx, -ry)
            val_key = (val, tie)
            if best_resource_val is None or val_key > best_resource_val:
                best_resource_val = val_key
        if best_resource_val is None:
            continue
        if best_val is None or best_resource_val > best_val:
            best_val = best_resource_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]