def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_pos = (ox, oy)

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources we are closer to; also bias toward central-ish to reduce long detours
            central_bias = abs(rx - (w // 2)) + abs(ry - (h // 2))
            key = (do <= ds, ds, central_bias, rx, ry)  # deterministic tie-break
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: head to the opponent's side deterministically
        tx = w - 1 if sx < (w // 2) else 0
        ty = h - 1 if sy < (h // 2) else 0

    cur_dist = man(sx, sy, tx, ty)
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) == opp_pos:
            continue
        d = man(nx, ny, tx, ty)
        # Strongly prefer reducing distance; small deterministic tie-breakers
        dist_gain = cur_dist - d
        score = (-dist_gain, d, abs(nx - (w // 2)) + abs(ny - (h // 2)), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]