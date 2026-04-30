def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = [(p[0], p[1]) for p in observation["resources"]]
    gw, gh = observation["grid_width"], observation["grid_height"]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles

    def mindist_to_resources(nx, ny):
        if not resources:
            return 999
        d = 999
        for rx, ry in resources:
            dx, dy = nx - rx, ny - ry
            dd = (dx * dx + dy * dy)
            if dd < d:
                d = dd
        return d ** 0.5

    def mindist_to_opponent(nx, ny):
        dx, dy = nx - ox, ny - oy
        return (dx * dx + dy * dy) ** 0.5

    rem = observation.get("remaining_resource_count", len(resources))
    risk_weight = 0.6 if rem > 4 else 0.25

    best = None
    best_score = -1e18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue
        if nx == ox and ny == oy:
            continue  # avoid stepping onto opponent
        dres = mindist_to_resources(nx, ny)
        dop = mindist_to_opponent(nx, ny)
        on_res = 1.0 if (nx, ny) in set(resources) else 0.0

        score = (-dres) + risk_weight * dop + 2.0 * on_res
        # If opponent is very close, slightly prefer moves that increase separation
        if mindist_to_opponent(x, y) < 2.0:
            score += 0.8 * dop

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]