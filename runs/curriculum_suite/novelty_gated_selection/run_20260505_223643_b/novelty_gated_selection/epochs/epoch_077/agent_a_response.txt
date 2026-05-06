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
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def sqd(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        return dx * dx + dy * dy

    opp_best_dist = None
    for rx, ry in resources:
        d = sqd(ox, oy, rx, ry)
        if opp_best_dist is None or d < opp_best_dist:
            opp_best_dist = d

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        nearest_self = None
        max_adv = None
        for rx, ry in resources:
            ds = sqd(nx, ny, rx, ry)
            if nearest_self is None or ds < nearest_self:
                nearest_self = ds
            adv = None
            do = sqd(ox, oy, rx, ry)
            adv = do - ds  # positive means resource is closer to us than to opponent
            if max_adv is None or adv > max_adv:
                max_adv = adv

        dist_to_opp = sqd(nx, ny, ox, oy)
        # Strongly prefer taking/keeping a relative advantage; also keep some spacing from opponent.
        score = (max_adv * 1000) + (dist_to_opp * 3) - (nearest_self if nearest_self is not None else 0) - (opp_best_dist * 0.001 if opp_best_dist else 0)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-breaker: prefer staying if equal advantage, else lexicographic
            if best_move == (0, 0) and (dx, dy) != (0, 0):
                continue
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]