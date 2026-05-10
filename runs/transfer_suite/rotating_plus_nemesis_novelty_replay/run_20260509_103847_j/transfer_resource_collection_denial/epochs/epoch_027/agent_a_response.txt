def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res_set = set(tuple(p) for p in resources)

    # Pick a contestable target if possible; otherwise pick best compromise.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer: we are at least as close; then shortest self distance; then minimize "opponent advantage"
        if sd <= od:
            key = (0, sd, od - sd, rx, ry)
        else:
            key = (1, od, sd - od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Evaluate immediate moves (with diagonals) deterministically.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue

        self_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Contest pressure: if we fall behind the opponent on this target, penalize.
        behind = max(0, self_d - opp_d)
        # Resource pickup preference.
        pickup = 1 if (nx, ny) in res_set else 0
        # Mild penalty for moving away from target and into proximity with opponent (to reduce "free" captures).
        dist_to_opp = man(nx, ny, ox, oy)

        score = (pickup * 100000) - self_d * 100 - behind * 1000 - dist_to_opp * 2

        # Tie-break deterministically: prefer moves that reduce x then y delta magnitude.
        tie = (abs(dx), abs(dy), dx, dy)
        full = (score, -tie[0], -tie[1], -tie[2], -tie[3])

        if best_score is None or full > best_score:
            best_score = full
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]