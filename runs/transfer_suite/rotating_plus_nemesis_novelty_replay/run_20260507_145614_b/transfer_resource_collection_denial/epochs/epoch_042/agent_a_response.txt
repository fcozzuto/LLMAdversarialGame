def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any((sx, sy) == tuple(r) for r in resources):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    # If no resources are visible, just move toward opponent's starting region center to avoid corner trapping.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        target_dx = 0 if sx == tx else (1 if tx > sx else -1)
        target_dy = 0 if sy == ty else (1 if ty > sy else -1)
        for dx, dy in deltas:
            if (dx, dy) == (target_dx, target_dy) and in_bounds(sx + dx, sy + dy):
                return [dx, dy]
        for dx, dy in deltas:
            if in_bounds(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        # Greedy "race" heuristic: prefer moves that make us closer than opponent to some resource,
        # while still progressing toward it; small repulsion from opponent to reduce sweep-row interceptions.
        opp_repulse = -1.0 / (cheb(nx, ny, ox, oy) + 1)

        best_resource = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Encourage winning the race and then quickly collecting.
            # If opponent already closer (opd - myd <= 0), deprioritize unless we can still flip within remaining turns.
            race = (opd - myd)
            urgency = myd
            flip_bonus = 0
            if race <= 0 and turns_remaining is not None:
                # If we can't arrive before they can, penalize harder; if we can, soften the penalty.
                if myd > opd:
                    flip_bonus = -30
                elif myd <= opd:
                    flip_bonus = 10

            val = 100 * race - 2 * urgency + flip_bonus

            # Strongly prefer immediate collection
            if myd == 0:
                val += 10**6

            if val > best_resource:
                best_resource = val

        # Slight preference for moving toward the best target direction: maximize best_resource, then closeness to opponent's nearer resource.
        total_val = best_resource + opp_repulse
        if total_val > best_val:
            best_val = total_val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]