def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = [0, 0]

    # Choose target cell among remaining resources by relative advantage
    # tie-break: prefer closer to self, then lexicographic.
    def target_order():
        if not resources:
            tx, ty = (w - 1, h - 1) if sx < w // 2 else (0, 0)
            return (tx, ty)
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Higher is better; minimize negative advantage => maximize advantage
            adv = (do - ds)  # we want do - ds large => we are closer
            # If both can reach, bias to faster self collection.
            score = (adv, -ds, -rx, -ry)
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        return best[1]

    tx, ty = target_order()

    # Evaluate immediate moves with a deterministic heuristic:
    # prefer moving toward target; also avoid cells that are obstacles.
    # incorporate opponent distance to encourage faster interception of the target.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # If no resources, head to opposite corner deterministically.
        if resources:
            ds_next = man(nx, ny, tx, ty)
            do_next = man(ox, oy, tx, ty)
            # Encourage getting closer than opponent (or at least not falling behind)
            rel = (do_next - ds_next)
            # Small penalty for moving away from target
            move_score = (rel, -ds_next)
        else:
            ds_next = man(nx, ny, tx, ty)
            move_score = (-(ds_next), -nx, -ny)

        # Tie-break deterministically: prefer lower dx, then lower dy
        # by embedding them as negatives (since we compare tuples).
        tie = (-dx, -dy)
        score = (move_score, tie)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move