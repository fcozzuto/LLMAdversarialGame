def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no visible resources, drift to center but still bias away from opponent.
    if not resources:
        targets = [(w // 2, h // 2), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
        best_move, best_val = (0, 0), None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            tx, ty = max(targets, key=lambda p: (-(abs(p[0]-ox)+abs(p[1]-oy)), -abs(p[0]-nx)-abs(p[1]-ny)))
            val = abs(nx - tx) + abs(ny - ty) - 0.2 * (abs(nx - ox) + abs(ny - oy))
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Race heuristic: for each next move, pick the resource that maximizes advantage vs opponent.
    def score_for_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        best = None
        for r in resources:
            our = dist((nx, ny), r)
            opp = dist((ox, oy), r)
            # Prefer taking a resource we can reach sooner (or at least tie),
            # then prefer closer resources to finish faster.
            adv = (opp - our)
            val = (-adv, our)  # smaller is better: maximize adv, then minimize our
            if best is None or val < best:
                best = val
        return best

    best_val, best_move = None, (0, 0)
    for dx, dy in legal:
        val = score_for_move(dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]