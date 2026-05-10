def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = [0, 0]
    my_next_candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_next_candidates.append((dx, dy, nx, ny))
    if not my_next_candidates:
        return [0, 0]

    # Score: maximize advantage and closeness to the best attainable resource.
    # Advantage term makes us prefer resources we can reach before the opponent.
    for dx, dy, nx, ny in my_next_candidates:
        best_local = None
        for rx, ry in resources:
            if isinstance(rx, (list, tuple)) and len(rx) >= 2:
                rx, ry = int(rx[0]), int(rx[1])
            else:
                rx, ry = int(rx), int(ry)
            if (rx, ry) in obs:
                continue
            myd = dist((nx, ny), (rx, ry))
            oppd = dist((ox, oy), (rx, ry))
            # Prefer being strictly faster; otherwise still prefer being closer than opponent.
            adv = oppd - myd  # positive if we are closer/faster
            # Slight bias to reduce distance to any resource if no clear advantage.
            score = adv * 100 - myd
            # Prefer collecting on this move if adjacent/at resource
            if myd == 0:
                score += 100000
            # Tie-break deterministically toward smaller myd then resource order
            key = (score, -myd)
            if best_local is None or key > best_local[0]:
                best_local = (key, (rx, ry))
        score = best_local[0][0] if best_local else -10**9
        # Prefer moves that are more "direct": lower my distance to the best resource chosen above.
        # Deterministic tie-break by dx,dy ordering.
        tie = (score, -abs(dx), -abs(dy), dx, dy)
        if best_score is None or tie > best_score:
            best_score = tie
            best_move = [dx, dy]

    return best_move