def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource we are "most advantaged" for: minimize (dist_self - dist_opp).
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        key = (man((sx, sy), (rx, ry)) - man((ox, oy), (rx, ry)),
               man((sx, sy), (rx, ry)), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        reach = 1 if (nx == tx and ny == ty) else 0
        # Prefer reaching resource; then reduce distance; then keep away from opponent.
        score_key = (-reach, d_self, -d_opp, dx, dy)
        if best_score is None or score_key < best_score:
            best_score = score_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]