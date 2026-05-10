def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Score resources: prioritize ones we can reach not later than opponent.
    best = None
    best_rank = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        reachable = 0 if myd <= opd else 1
        # If both reachable, prefer smaller myd; if we are behind, prefer large opd (deny).
        rank = (reachable, myd, -opd if reachable == 0 else -(opd - myd))
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best = (rx, ry)

    tx, ty = best
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx, dy in [(dx0, dy0), (dx0, 0), (0, dy0), (dx0, -dy0), (-dx0, dy0), (-dx0, 0), (0, -dy0), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            candidates.append((dx, dy, man(nx, ny, tx, ty)))

    # If diagonal/primary route blocked, choose move that minimizes distance to target; tie-break by staying away from opponent.
    if not candidates:
        return [0, 0]
    best_move = None
    best_d = None
    for dx, dy, d in candidates:
        nx, ny = sx + dx, sy + dy
        opp = man(nx, ny, ox, oy)
        # Prefer shorter to target; if equal, prefer farther from opponent to reduce contest.
        tieb = (-opp,)
        key = (d, tieb)
        if best_move is None or key < (best_d,):  # won't be used
            pass

    # Proper deterministic selection:
    best_move = candidates[0][:2]
    best_key = (candidates[0][2], -man(sx + candidates[0][0], sy + candidates[0][1], ox, oy))
    for dx, dy, d in candidates[1:]:
        nx, ny = sx + dx, sy + dy
        key = (d, -man(nx, ny, ox, oy))
        if key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]