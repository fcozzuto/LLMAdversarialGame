def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target that we can reach no later than opponent; tie-break by our distance and then cell coords.
    best = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        race = 0 if sd <= od else 1
        key = (race, sd, -od, tx, ty)
        if best is None or key < best:
            best = key
            target = (tx, ty)

    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**9, 0, 0)

    # Evaluate one-step moves by estimated improvement in our winning margin toward target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if (nx, ny) == (tx, ty):
            return [dx, dy]

        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer better race margin (smaller sd when sd<=od; if we're behind, prefer reducing od-sd).
        margin = (od - sd)
        # Also keep movement aligned toward target to avoid dithering.
        align = -((tx - nx) * (tx - sx) + (ty - ny) * (ty - sy) >= 0)
        # Combine with obstacle-safe tiebreak.
        key = (0 if sd <= od else 1, -margin, sd, align, nx, ny)
        if key < best_move:
            best_move = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]