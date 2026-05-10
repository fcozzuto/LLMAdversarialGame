def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    opp_mob = mobility(ox, oy)

    best_score = None
    best_move = [0, 0]
    d0 = manh(sx, sy, ox, oy)

    # Deterministic tie-break order: fixed move order; compare scores only.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        d = manh(nx, ny, ox, oy)
        my_mob = mobility(nx, ny)
        e = edge_dist(nx, ny)

        if is_evader:
            # Evader: maximize distance; avoid getting trapped near edges while staying mobile.
            # Mildly prefer moves that increase opponent mobility reduction (keeps escape routes open for us).
            score = (d, my_mob, e, -abs(nx - ox) - abs(ny - oy))
            # Convert to deterministic ordering using tuple comparison later.
            key = score
            if best_score is None or key > best_score:
                best_score, best_move = key, [dx, dy]
        else:
            # Pursuer: minimize distance; reduce opponent's "effective freedom" proxy by approaching their nearest border.
            # Prefer moves that keep us mobile and bias toward pinning near edges (wall runner).
            # Also include a small alignment term to reduce diagonal drift.
            pin = min(ox, oy, w - 1 - ox, h - 1 - oy)
            align = -abs(nx - ox) - abs(ny - oy)
            score = (-d, my_mob, pin, align, -opp_mob)
            key = score
            if best_score is None or key > best_score:
                best_score, best_move = key, [dx, dy]

    # Fallback: if all moves blocked (shouldn't happen), stay.
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]