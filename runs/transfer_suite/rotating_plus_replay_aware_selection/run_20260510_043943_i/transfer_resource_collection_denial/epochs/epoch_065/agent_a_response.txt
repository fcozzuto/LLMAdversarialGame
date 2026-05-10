def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = int(observation.get("turns_remaining", 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def heuristic_best_move():
        deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best_key = None
        best = [0, 0]
        # Prefer earlier grabs; if not possible, deny by moving toward resources opponent targets sooner.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                nx, ny = sx, sy
                dx, dy = 0, 0
            # compute best resource after this move
            for rx, ry in resources:
                if not cell_ok(rx, ry):
                    continue
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # Advantage: lower sd first, but strongly prefer sd < od (get there first)
                # Use remaining turns to emphasize finishing quickly.
                if turns_remaining > 0:
                    fin_self = sd - (turns_remaining // 10)
                    fin_opp = od - (turns_remaining // 10)
                else:
                    fin_self = sd
                    fin_opp = od
                adv = fin_opp - fin_self  # positive if we are closer (earlier)
                # Key: maximize adv, then minimize our distance, then prefer reducing Manhattan to resource.
                # Deterministic tie-break by coordinates.
                key = (-adv, sd, od, rx, ry, dx, dy)
                # Convert to minimization by negating adv in first position above
                if best_key is None or key < best_key:
                    best_key = key
                    best = [dx, dy]
        return best

    if not resources:
        return [0, 0]
    return heuristic_best_move()