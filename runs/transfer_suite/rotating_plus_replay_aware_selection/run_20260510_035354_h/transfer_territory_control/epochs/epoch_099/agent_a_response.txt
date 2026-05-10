def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ax, ay, ox, oy = int(ax), int(ay), int(ox), int(oy)

    def toset(lst):
        s = set()
        if not lst:
            return s
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    self_set = toset(observation.get("self_territory"))
    opp_set = toset(observation.get("opponent_territory"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a deterministic target: nearest unclaimed cell; if none, nearest opponent territory cell; else empty.
    target = None
    if unclaimed:
        best = None
        for tx, ty in unclaimed:
            if (tx, ty) in obstacles:
                continue
            d = md(ax, ay, tx, ty)
            key = (d, ty, tx)
            if best is None or key < best:
                best = key
                target = (tx, ty)
    elif opp_set:
        best = None
        for tx, ty in opp_set:
            if (tx, ty) in obstacles:
                continue
            d = md(ax, ay, tx, ty)
            key = (d, ty, tx)
            if best is None or key < best:
                best = key
                target = (tx, ty)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        score = 0.0

        # Immediate benefit for claiming/flipping.
        if cell in opp_set:
            score += 6.0
        elif cell in unclaimed:
            score += 3.0
        elif cell in self_set:
            score += 1.0

        # Route towards chosen target.
        if target is not None:
            tx, ty = target
            score += -0.7 * md(nx, ny, tx, ty)

        # Micro-tactics: avoid walking directly onto opponent if it offers no upside;
        # encourage approaching opponent only when targeting exists.
        d_to_opp = md(nx, ny, ox, oy)
        if target is not None and cell in opp_set:
            score += 0.3 * d_to_opp
        else:
            score += 0.02 * d_to_opp

        # Deterministic tie-break by move order.
        key = score
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]