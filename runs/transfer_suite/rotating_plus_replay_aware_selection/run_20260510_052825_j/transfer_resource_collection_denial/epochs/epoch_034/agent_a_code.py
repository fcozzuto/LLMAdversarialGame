def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    remaining = observation.get("remaining_resource_count", len(resources))
    turns = observation.get("turns_remaining", 0)
    few = (remaining <= 3) or (turns <= 6)

    # Choose best immediate target: maximize advantage, but prefer closer when few left.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles or not (0 <= rx < w and 0 <= ry < h):
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # If we are far behind, deprioritize; if close, boost.
        adv = (od - sd)
        val = adv * (3.0 if not few else 2.0) - sd * (0.6 if not few else 1.1)
        if sd <= 1:
            val += 3.0
        if od <= 1 and sd > od:
            val -= 4.0
        # Deterministic tie-break
        val += -0.001 * (rx * 10 + ry)
        if best is None or val > best[0]:
            best = (val, rx, ry)
    if best is None:
        return [0, 0]

    _, tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If opponent is closer to the chosen target by a lot and few aren't left, reconsider quickly.
    # (Cheap reassessment using same heuristic on the fly.)
    if not few:
        best2 = best
        for rx, ry in resources:
            if (rx, ry) in obstacles or not (0 <= rx < w and 0 <= ry < h):
                continue
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            val = adv * 3.2 - sd * 0.8
            if sd <= 1:
                val += 2.0
            if od <= 1 and sd > od:
                val -= 4.0
            val += -0.001 * (rx * 10 + ry)
            if best2 is None or val > best2[0]:
                best2 = (val, rx, ry)
        best = best2
        _, tx, ty = best

    # Greedy step: choose move that minimizes our distance to target and avoids obstacles.
    best_step = (None, None, None)  # (score, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd = man(nx, ny, tx, ty)
        od = man(nx, ny, ox, oy)  # small secondary: drift away from opponent pressure
        # Primary: reduce distance; secondary: prevent getting too close to opponent pathing.
        score = -sd * 10.0 + (od * 0.05) + (-0.001 * (dx * 3 + dy))
        if best_step[0] is None or score > best_step[0]:
            best_step = (score, dx, dy)

    if best_step[1] is None:
        return [0, 0]
    return [int(best_step[1]), int(best_step[2])]