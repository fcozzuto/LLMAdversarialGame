def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a resource that we can reach sooner, but also that helps in scarcity
    best = None
    best_key = None
    remaining = observation.get("remaining_resource_count", len(resources))
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer winning the contest (large ds-do), then closer overall, then tie-break deterministically
        key = (do - ds, -ds, -(rx + 31 * ry), ds - do)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If opponent is very close to target, bias to cutting the corner (diagonal/axis step toward target)
    opp_ds = dist(ox, oy, tx, ty)
    aggressive = (opp_ds <= 2 and remaining <= max(6, len(resources)))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = dist(nx, ny, tx, ty)
        # small penalty for staying; big reward for reducing distance
        delta = dist(sx, sy, tx, ty) - ns
        score = (delta, -ns, -abs(dx) - abs(dy), 1 if (nx == tx or ny == ty) else 0)
        if aggressive and dx != 0 and dy != 0:
            score = (score[0] + 0.5, score[1], score[2], score[3])
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]