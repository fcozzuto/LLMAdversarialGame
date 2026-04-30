def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Choose resource that maximizes advantage: closer to me than to opponent.
    best = None
    best_key = None
    mypos = (sx, sy)
    opppos = (ox, oy)
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        md = dist2(mypos, (rx, ry))
        od = dist2(opppos, (rx, ry))
        # Prefer winning race: minimize my dist, while maximizing opponent disadvantage.
        key = (od - md, -md, md, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    # If no resources, head to center-ish deterministically.
    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    # Candidate moves (including stay), avoid obstacles if possible.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # Score move by: get closer to target, but also keep opponent farther.
            my_to = dist2((nx, ny), (tx, ty))
            opp_to = dist2(opppos, (tx, ty))
            # Also slightly prefer moves that increase distance between agents.
            agent_sep = dist2((nx, ny), opppos)
            moves.append((my_to, -opp_to, -agent_sep, dx, dy))

    # If all blocked (rare), allow stay.
    if not moves:
        return [0, 0]

    # Deterministic best: lexicographic by constructed tuple.
    moves.sort()
    return [moves[0][3], moves[0][4]]