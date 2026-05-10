def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def exits(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    # Deterministic tie-break: prefer lexicographically smaller move (dx,dy) by sorting.
    candidates = []
    ordered_moves = sorted(moves)

    if is_evader:
        # Evader: maximize distance to pursuer; prefer moves with more future exits.
        for dx, dy in ordered_moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            candidates.append((dist, exits(nx, ny), -abs(nx - ox) - abs(ny - oy), dx, dy))
        if not candidates:
            return [0, 0]
        best = max(candidates)
        return [int(best[3]), int(best[4])]

    # Pursuer: minimize distance; also use one-step lookahead to reduce opponent escape.
    for dx, dy in ordered_moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist_after = cheb(nx, ny, ox, oy)
        # Assume opponent will move to maximize our distance next turn.
        worst_dist = -1
        for odx, ody in ordered_moves:
            ex, ey = ox + odx, oy + ody
            if not ok(ex, ey):
                continue
            d = cheb(nx, ny, ex, ey)
            if d > worst_dist:
                worst_dist = d
        if worst_dist < 0:
            worst_dist = dist_after
        # Primary: reduce current distance; Secondary: keep opponent from increasing it too much; Tertiary: fewer escapes.
        candidates.append((-dist_after, -(worst_dist - dist_after), exits(nx, ny), dx, dy))
    if not candidates:
        return [0, 0]
    best = max(candidates)
    return [int(best[3]), int(best[4])]