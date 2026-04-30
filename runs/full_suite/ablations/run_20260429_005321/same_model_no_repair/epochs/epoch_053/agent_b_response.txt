def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]

    blocked = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def metric(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # diagonal-allowed

    def adj_obs(x, y):
        # small penalty for moving adjacent to obstacles (reduces getting trapped)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in blocked:
                    return 1
        return 0

    # Pick a target where we are relatively closer than the opponent (contest resources deterministically)
    best_t = None
    best_score = -10**18
    for tx, ty in resources:
        if (tx, ty) in blocked:
            continue
        myd = metric((sx, sy), (tx, ty))
        opd = metric((ox, oy), (tx, ty))
        score = (opd - myd) * 10 - myd  # prefer being ahead; then closer
        if score > best_score or (score == best_score and myd < metric((sx, sy), best_t)):
            best_score = score
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    opd = metric((ox, oy), (tx, ty))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        myd_next = metric((nx, ny), (tx, ty))
        val = (opd - myd_next) * 10 - myd_next
        if (nx, ny) == (tx, ty):
            val += 1000
        val -= 2 * adj_obs(nx, ny)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move