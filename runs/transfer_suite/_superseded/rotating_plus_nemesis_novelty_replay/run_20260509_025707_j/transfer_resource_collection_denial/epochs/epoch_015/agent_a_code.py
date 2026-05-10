def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    # Prefer resources where we are strictly closer; otherwise still pick best compromise.
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Higher is better: race advantage, then closer, then prefer smaller x+y (more central-ish early)
        key = ((od > sd) - (od < sd), -(sd), -(rx + ry))
        # If race advantage same bucket, use raw advantage magnitude
        adv = od - sd
        key2 = (adv, -sd, -(rx + ry))
        k = key2 if abs(adv) != 0 else key
        if best_key is None or k > best_key:
            best_key = k
            best_r = (rx, ry)

    tx, ty = best_r

    # Two-step deterministic lookahead: choose move that maximizes (our progress - opponent progress) to target,
    # with penalty if the immediate cell is worse than staying.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        our1 = man(nx, ny, tx, ty)
        opp1 = man(ox, oy, tx, ty)
        score = (opp1 - our1, -our1, -abs(nx - tx) - abs(ny - ty))

        # If we land on a resource, boost strongly.
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in set(map(tuple, resources)):
            score = (score[0] + 1000, score[1], score[2] - 1000)

        # Micro-adjustment: avoid moves that make us farther from all resources.
        sum_dist = 0
        for rx, ry in resources:
            sum_dist += man(nx, ny, rx, ry)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]