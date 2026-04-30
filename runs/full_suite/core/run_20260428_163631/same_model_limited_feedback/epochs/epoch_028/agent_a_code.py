def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    me_on_resource = (sx, sy) in set(tuple(p) for p in resources)
    if me_on_resource:
        return [0, 0]

    # Choose best target deterministically
    target = None
    best = None
    res_set = [tuple(p) for p in resources]
    for r in res_set:
        dme = dist2((sx, sy), r)
        dob = dist2((ox, oy), r)
        score = dme - 0.35 * dob  # lower is better
        if best is None or score < best or (score == best and (dme < dist2((sx, sy), target))):
            best = score
            target = r

    if target is None:
        return [0, 0]

    tx, ty = target

    # Candidate moves: prefer those that get closer; avoid obstacles
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # Prefer closer to target, and slight preference to move away from opponent
            d_before = dist2((sx, sy), (tx, ty))
            d_after = dist2((nx, ny), (tx, ty))
            opp_before = dist2((ox, oy), (tx, ty))
            opp_after = dist2((nx, ny), (tx, ty))
            # Deterministic tie-break via move order by dx,dy encoded
            move_score = (d_after, -((opp_after - opp_before) * 0.0), abs(dx) + abs(dy), dx, dy)
            moves.append((move_score, [dx, dy]))

    if not moves:
        return [0, 0]
    moves.sort(key=lambda x: x[0])
    return moves[0][1]