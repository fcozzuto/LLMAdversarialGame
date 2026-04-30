def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_r = None
        best_v = -10**9
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            v = (do - ds) * 1000 - ds  # deny-first
            if v > best_v or (v == best_v and (rx, ry) < best_r):
                best_v = v
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = 3, 3  # deterministic fallback

    best_move = (0, 0)
    best_val = -10**18
    cur_d = dist((sx, sy), (tx, ty))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        nd = dist((nx, ny), (tx, ty))
        # Move value: prefer reducing distance and increasing opponent disadvantage
        do = dist((ox, oy), (tx, ty))
        ds_next = nd
        val = (do - ds_next) * 1000 + (cur_d - nd) * 10
        # Small deterministic tie-break: prefer lexicographically smaller move
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]