def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target we are winning toward; tie-break by closer overall then coordinates.
    best_target = None
    best_key = None
    for x, y in resources:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        key = (od - sd, -sd, -od, -x, -y)  # prefer we are ahead; then nearer
        if best_key is None or key > best_key:
            best_key = key
            best_target = (x, y)

    tx, ty = best_target

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    # Evaluate moves: take resource if available; otherwise maximize advantage after move.
    res_set = set(resources)
    best_move = (0, 0)
    best_val = None
    for dx, dy, nx, ny in moves:
        gain = 1 if (nx, ny) in res_set else 0
        sd = abs(tx - nx) + abs(ty - ny)
        od = abs(tx - ox) + abs(ty - oy)
        # After moving, prefer reducing our distance more than opponent's to the same target.
        val = (gain * 10, (od - (sd + 0)), -sd, -abs(nx - tx) - abs(ny - ty), -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]