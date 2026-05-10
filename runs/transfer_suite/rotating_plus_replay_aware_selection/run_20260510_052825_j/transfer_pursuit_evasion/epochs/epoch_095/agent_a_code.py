def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    am_evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("hider" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    # If directly adjacent, capture if possible (pursuer). For evader, avoid capture.
    best_move = [0, 0]
    best_score = None

    # Bias "cutoff": move toward the opponent-projected edge band relative to our side.
    # If opponent is nearer left edge, favor moving left when chasing; otherwise opposite.
    def edge_bias(x, y):
        left = x
        right = (w - 1 - x)
        top = y
        bot = (h - 1 - y)
        e = min(left, right, top, bot)
        return e

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if nx == ox and ny == oy:
            if not am_evader:
                return [dx, dy]
            # Evader: never move into capture if any alternative exists
            continue

        d = dist2(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)

        # Cutoff term: chase tends to reduce opponent distance-to-edge; evader tends to increase.
        opp_edge_dist = min(ox, w - 1 - ox, oy, h - 1 - oy)
        our_edge_dist = min(nx, w - 1 - nx, ny, h - 1 - ny)

        # Deterministic weighting.
        chase = (-d) + 0.35 * fn + 0.07 * (our_edge_dist - opp_edge_dist) - 0.03 * (abs(dx) + abs(dy))
        evade = (d) + 0.25 * fn + 0.07 * (opp_edge_dist - our_edge_dist) - 0.03 * (abs(dx) + abs(dy))
        score = evade if am_evader else chase

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move