def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        ds = dist((x, y), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources we can reach sooner; otherwise deny by choosing closer to us while still competitive.
        val = (do - ds) * 20 - ds
        # Slightly prefer nearer resources overall to reduce dithering.
        val += -0.1 * (rx + ry)
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r
    best_m = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        ds = dist((nx, ny), (tx, ty))
        do = dist((ox, oy), (tx, ty))
        # Try to increase our lead and decrease distance to target.
        score = (do - ds) * 30 - ds
        # Deterministic tie-break: favor staying still less, then lexicographic by move list order.
        if score > best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]