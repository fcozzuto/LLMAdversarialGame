def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(a, b, c, d):
        t1 = a - c
        if t1 < 0:
            t1 = -t1
        t2 = b - d
        if t2 < 0:
            t2 = -t2
        return t1 + t2

    # Target selection tuned to contest opponent sweep behavior:
    # prioritize resources that the opponent can reach relatively faster,
    # but also strongly prioritize resources on (or near) opponent's current row.
    best = None
    best_score = None
    for tx, ty in resources:
        ds = manh(sx, sy, tx, ty)
        do = manh(ox, oy, tx, ty)
        row_bias = 10 if ty == oy else 0
        near_row_bias = 3 if (ty == oy - 1 or ty == oy + 1) else 0
        score = (do - ds) * 4 + row_bias + near_row_bias - ds
        if best_score is None or score > best_score or (score == best_score and (ds < best[0] or (ds == best[0] and (ty, tx) < (best[1], best[2])))):
            best_score = score
            best = (ds, ty, tx, tx, ty)

    tx, ty = best[3], best[4]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = manh(nx, ny, tx, ty)
        # Tie-break: avoid drifting away from opponent's row contest
        row_cont = 0
        if ty == oy:
            row_cont = 1 if ny == oy else 0
        val = -d + row_cont
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]