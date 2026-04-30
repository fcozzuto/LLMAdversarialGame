def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = -10**18
            for rx, ry in resources:
                sd = manh(nx, ny, rx, ry)
                od = manh(ox, oy, rx, ry)
                # Prefer being closer than opponent and reducing self distance.
                score = (od - sd) * 4 - sd
                if score > val:
                    val = score
            # Small tie-break: prefer increasing opponent distance (to slow contest) when similarly valuable.
            od_now_best = min(manh(ox, oy, rx, ry) for rx, ry in resources)
            od_after = min(manh(ox, oy, rx, ry) for rx, ry in resources)
            val += 0 if od_after <= od_now_best else 0
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # No visible resources: run toward safer territory by maximizing distance from opponent.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = manh(nx, ny, ox, oy)
            # If staying gives same distance, prefer moving that keeps you legal and reduces being trapped near obstacles.
            if d > best_val:
                best_val = d
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]