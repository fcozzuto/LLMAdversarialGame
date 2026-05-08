def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    if (0, 0) not in moves:
        moves.append((0, 0))
    # Deterministic ordering preference: stay last
    moves.sort(key=lambda m: (m == (0, 0), m[0], m[1]))

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        opp_dmin = None  # for tie-breaking variety
        move_best = None

        for rx, ry in resources:
            dself = dist2(nx, ny, rx, ry)
            dopp = dist2(ox, oy, rx, ry)
            adv = dopp - dself  # higher is better (opponent farther than us)
            # If we are already at the resource next position, strongly prefer
            on = 1 if (nx, ny) == (rx, ry) else 0
            # Also slightly prefer closer resources to keep progressing deterministically
            score = (on, adv, -dself, rx, ry)
            if move_best is None or score > move_best:
                move_best = score
            if opp_dmin is None or dopp < opp_dmin:
                opp_dmin = dopp

        if move_best is None:
            continue
        # Prefer moves that create larger advantage; tie-break by lower opp distance (more likely to deny)
        final = (move_best[0], move_best[1], move_best[2], -opp_dmin)
        if best_score is None or final > best_score:
            best_score = final
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]