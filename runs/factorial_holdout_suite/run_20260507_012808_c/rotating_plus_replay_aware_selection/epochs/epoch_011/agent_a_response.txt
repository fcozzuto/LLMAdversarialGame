def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (0, 0) if (sx + sy) <= ((w - 1 - sx) + (h - 1 - sy)) else (w - 1, h - 1)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            key = (dist((nx, ny), (tx, ty)), dist((nx, ny), (ox, oy)))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Score resources by advantage (opp closer is bad). If no positive advantage exists, race nearest.
    best_target = None
    best_val = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer big advantage; also slightly prefer closer absolute to prevent stalling.
        val = (od - sd, -0.15 * sd)
        if best_val is None or val > best_val or (val == best_val and (rx, ry) < best_target):
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    # Choose move that reduces distance to target, but also avoids stepping closer to the opponent when we're behind.
    my_d = dist((sx, sy), (tx, ty))
    opp_d = dist((sx, sy), (ox, oy))
    behind = (dist((ox, oy), (tx, ty)) <= my_d)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nd = dist((nx, ny), (tx, ty))
        nod = dist((nx, ny), (ox, oy))
        # When behind, bias toward not giving the opponent an easy grab next step.
        penalty = 0.0
        if behind:
            penalty = 0.6 * (nod - opp_d)  # moving toward opponent increases penalty
        # Also encourage finishing line: tie-break with opponent distance first (more safety), then lexicographic move.
        key = (nd, penalty, -nod, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]