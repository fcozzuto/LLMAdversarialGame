def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    my2 = sx * sx + sy * sy

    def d2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Pick the best target by who can get it first; discourage far targets.
    best_t = None
    best_key = None
    my_pos = (sx, sy)
    opp_pos = (ox, oy)
    for r in resources:
        myd = d2(my_pos, r)
        opd = d2(opp_pos, r)
        # Primary: maximize distance advantage for us (opp further than us).
        # Secondary: prefer closer for us.
        key = (opd - myd, -myd)
        if best_key is None or key > best_key:
            best_key = key
            best_t = r

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        n_my = (nx, ny)
        # Evaluate: move that maximizes immediate win chances for target and keeps options.
        target_score = (d2(opp_pos, (tx, ty)) - d2(n_my, (tx, ty)))
        # Small shaping: reduce distance to target; and keep stable if tied.
        dist_pen = -d2(n_my, (tx, ty))
        tie_stable = -((dx != 0) or (dy != 0))
        score = (target_score, dist_pen, tie_stable)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]