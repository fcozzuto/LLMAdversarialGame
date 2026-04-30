def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Choose target: prefer nearest resource, tie-break by x then y for determinism
    if resources:
        best = None
        for r in resources:
            if best is None:
                best = r
            else:
                d = dist2(self_pos, r)
                bd = dist2(self_pos, best)
                if d < bd or (d == bd and (r[0], r[1]) < (best[0], best[1])):
                    best = r
        target = best
    else:
        # No resources visible: move toward opponent to contest space slightly
        target = opp_pos

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference order already from list; score moves by (best distance, then avoid obstacles, then distance to opponent)
    cur = tuple(self_pos)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = cur[0] + dx, cur[1] + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist2((nx, ny), target)
        od = dist2((nx, ny), opp_pos)
        # Primary: get closer to target; Secondary: keep away from opponent; Tertiary: deterministic via move order
        score = (nd, -od)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    # If all candidate moves were blocked, fall back to staying still
    return [int(best_move[0]), int(best_move[1])]