def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Pick target I can reach sooner than opponent; otherwise maximize advantage (opp_dist - self_dist).
    best_key = None
    best_t = (sx, sy)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist2((sx, sy), (rx, ry))
        od = dist2((ox, oy), (rx, ry))
        adv = od - sd
        # primary: reach-sooner flag, then advantage, then deterministic position tiebreak
        key = (0 if sd <= od else 1, -adv, ry, rx)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # If adjacent to any resource (including diagonal), step onto it deterministically.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in resources and (nx, ny) not in obstacles:
            return [dx, dy]

    # Otherwise, move that greedily reduces my distance to target; add slight tie-break away from opponent.
    chosen = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = dist2((nx, ny), (tx, ty))
        opd = dist2((nx, ny), (ox, oy))
        # Prefer closer to target; if equal, prefer increasing distance to opponent; deterministic move order by direction sum.
        key = (myd, -opd, abs(dx) + abs(dy), dx, dy)
        if chosen is None or key < chosen[0]:
            chosen = (key, [dx, dy])

    return chosen[1] if chosen is not None else [0, 0]