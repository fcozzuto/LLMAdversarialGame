def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        by = y1 - y2
        if by < 0: by = -by
        return ax + by

    # Choose a competitive target: prefer where we can arrive sooner (or deny opponent).
    best = None
    best_key = None
    for rx, ry in resources:
        ds = man(rx, ry, sx, sy)
        do = man(rx, ry, ox, oy)
        # primary: maximize (do - ds), secondary: smaller ds (closer), tertiary: lower coords
        key = (-(do - ds), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            x2, y2 = sx + dx, sy + dy
            if 0 <= x2 < w and 0 <= y2 < h and (x2, y2) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # One-step lookahead: pick move that improves our position vs target while considering opponent pressure.
    cur_ds = man(tx, ty, sx, sy)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        x2, y2 = sx + dx, sy + dy
        ds2 = man(tx, ty, x2, y2)
        do2 = man(tx, ty, ox, oy)  # opponent doesn't move this turn in our decision
        progress = cur_ds - ds2  # positive if we get closer
        # Score: maximize progress, then minimize our distance, then maximize denial (opponent farther), then stable order
        score = (-progress, ds2, -(do2 - ds2), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]