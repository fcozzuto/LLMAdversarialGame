def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # Deterministic edge/center pressure: move toward opponent's row/col while staying safe
        tx = 0 if ox < sx else (w - 1 if ox > sx else sx)
        ty = 0 if oy < sy else (h - 1 if oy > sy else sy)
        best = None
        for dx, dy, nx, ny in moves:
            d = man(nx, ny, tx, ty)
            key = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Heuristic: for each move, evaluate best resource we can "claim" relative to opponent.
    # Prefer: (1) making ourselves closer than opponent to a resource, (2) reducing distance to that resource,
    # (3) resources that are far from opponent when we can't beat them.
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        # compute local best target score for this move
        best_score = None
        best_target = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # positive if we are closer than opponent after this move
            lead = od - sd
            # Score components:
            # primary: maximize lead, then minimize our distance, then deterministic tie-break by coordinates
            score = (lead, -sd, rx, ry, sd - od)
            if best_score is None or score > best_score:
                best_score = score
                best_target = (rx, ry)
        rx, ry = best_target
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)
        # discourage moves that bring us closer to opponent without improving claim
        avoid_opp = man(nx, ny, ox, oy) <= 2 and (od - sd) < 1
        key = (-best_score[0], sd, -((od - sd)), (rx + ry), dx, dy, 1 if avoid_opp else 0)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]