def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = observation["resources"] if observation["resources"] is not None else []
    target = None
    best = None
    for rx, ry in resources:
        dx1, dy1 = rx - sx, ry - sy
        dself = dx1 * dx1 + dy1 * dy1
        dx2, dy2 = rx - ox, ry - oy
        dopp = dx2 * dx2 + dy2 * dy2
        score = (dself - dopp, dself, rx, ry)  # prioritize resources we can reach first
        if best is None or score < best:
            best = score
            target = (rx, ry)
    if target is None:
        return [0, 0]
    rx, ry = target

    delta_options = []
    # Prefer movement that approaches target: deterministic ordered deltas
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) not in obstacles:
                    delta_options.append((dx, dy))
    if not delta_options:
        return [0, 0]

    def next_dist2(dx, dy):
        nx, ny = sx + dx, sy + dy
        ddx, ddy = rx - nx, ry - ny
        return ddx * ddx + ddy * ddy

    delta_options.sort(key=lambda d: (next_dist2(d[0], d[1]), d[0], d[1]))
    best_delta = delta_options[0]
    return [int(best_delta[0]), int(best_delta[1])]