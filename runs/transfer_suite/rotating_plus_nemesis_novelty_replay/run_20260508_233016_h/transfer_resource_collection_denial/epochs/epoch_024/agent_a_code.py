def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_rank = None
    for (rx, ry) in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)

        # Prefer resources I can reach first; otherwise deny by maximizing opponent delay.
        # Tie-break: smaller my distance; then farther from opponent.
        reachable = 1 if myd <= opd else 0
        rank = (
            0 if reachable else 1,
            myd,                      # if reachable, fastest
            -opd if reachable else myd + (opd - myd) * 2  # if not, punish for being behind
        )
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best = (rx, ry)

    tx, ty = best

    # Greedy move toward target with deterministic tie-breaking, avoiding obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Small "anti-stay" bias and proximity score.
        my_next = man(nx, ny, tx, ty)
        # Deny factor: slightly prefer moves that increase distance to target for opponent.
        opp_next = man(ox, oy, tx, ty)
        score = (my_next, -opp_next, 1 if (dx == 0 and dy == 0) else 0, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]