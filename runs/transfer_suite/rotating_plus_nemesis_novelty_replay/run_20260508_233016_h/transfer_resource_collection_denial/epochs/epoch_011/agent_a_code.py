def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obst_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obst_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Choose a target resource with a bias to "we can get it first"
    best = None
    best_key = None
    for rx, ry in resources:
        sd = d(sx, sy, rx, ry)
        od = d(ox, oy, rx, ry)
        # primary: we are closer; secondary: absolute urgency
        ahead = sd - od  # negative means we are closer
        key = (abs(od - sd), ahead, od, sd, rx, ry)
        # Want smallest abs gap, but prefer negative ahead; this key makes negative ahead earlier after abs-gap
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            score = -10**9
        else:
            # One-step lookahead: prefer moving closer to target while also increasing opponent distance to it
            my_dist = d(nx, ny, tx, ty)
            opp_dist = d(ox, oy, tx, ty)
            cur_my = d(sx, sy, tx, ty)
            # Encourage taking the lead and reducing opponent's ability to race it (even without predicting their move)
            lead_gain = (cur_my - my_dist) - 0.3 * (opp_dist - d(ox, oy, tx, ty))
            # Also softly avoid moving into the opponent's immediate vicinity
            opp_close = -0.08 * d(nx, ny, ox, oy)
            # Tie-break deterministically toward staying and toward smaller dx,dy pattern
            tie = -(dx * 10 + dy)
            score = lead_gain - 1.0 * my_dist + opp_close + 0.01 * tie

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]