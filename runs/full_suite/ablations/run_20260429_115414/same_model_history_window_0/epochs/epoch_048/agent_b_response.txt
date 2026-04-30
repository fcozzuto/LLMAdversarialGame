def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        return nx, ny

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Pick a deterministic best resource: min dist2, then min y, then min x
    if resources:
        best = None
        for rx, ry in resources:
            d = dist2((sx, sy), (rx, ry))
            key = (d, ry, rx)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = ox, oy  # no resources: hover toward opponent

    opp = (ox, oy)
    neighbors = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in neighbors:
        nx = sx + dx
        ny = sy + dy
        loc = clamp(nx, ny)
        if loc is None:
            continue
        if loc in obstacles:
            continue
        if loc == opp:  # avoid collision
            continue

        # Directional greedy toward target with slight anti-opponent pressure
        to_target = dist2(loc, (tx, ty))
        to_opp = dist2(loc, opp)
        score = (to_target, -to_opp, dy, dx)  # lexicographic: smaller to_target, larger to_opp
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]