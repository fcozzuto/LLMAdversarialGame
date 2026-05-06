def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (0, 1), (-1, 1), (1, 1)]

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Pick up to 5 candidate resources; for each, measure advantage vs opponent.
    # Advantage favors resources closer to us than to opponent.
    cand = []
    for (rx, ry) in resources:
        ds = d2(sx, sy, rx, ry)
        do = d2(ox, oy, rx, ry)
        adv = do - ds  # bigger => we are relatively closer
        cand.append((adv, ds, rx, ry))
    cand.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    cand = cand[:5]

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Keep away from opponent if they are near our best targets.
        opp_dist = d2(nx, ny, ox, oy)
        # Main objective: improve advantage to our chosen target set.
        score = 0
        for adv, ds, rx, ry in cand:
            ds2_ = d2(nx, ny, rx, ry)
            new_adv = d2(ox, oy, rx, ry) - ds2_
            score = max(score, new_adv)  # best improvement among candidates
        # Penalties/bonuses to reduce tie and avoid opponent snatching.
        score += -0.05 * opp_dist
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]