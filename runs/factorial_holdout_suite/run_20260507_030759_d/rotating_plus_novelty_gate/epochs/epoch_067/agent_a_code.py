def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources", []) or []
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    resset = set(res)

    if (sx, sy) in resset:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                legal.append((0, 0))
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                legal.append((dx, dy))
    if not legal or not res:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return max(abs(ax - bx), abs(ay - by))  # diagonal-capable distance

    # Choose a resource where we have positive distance advantage vs opponent.
    best_target = None
    best_val = None
    for r in res:
        dself = dist((sx, sy), r)
        dopp = dist((ox, oy), r)
        val = (dopp - dself, -dself)  # maximize advantage, then closer
        if best_val is None or val > best_val:
            best_val, best_target = val, r

    tx, ty = best_target

    # If we can take any resource this turn, do so; else move greedily toward the chosen target,
    # with a small penalty if the move reduces our advantage.
    best_move = None
    best_cmp = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in resset:
            return [dx, dy]
        dnew = dist((nx, ny), (tx, ty))
        adv_new = dist((ox, oy), (tx, ty)) - dnew
        # Also discourage stepping next to obstacles lightly by checking occupancy in 8-neighborhood.
        near_obst = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                px, py = nx + ex, ny + ey
                if (px, py) in obst:
                    near_obst += 1
        cmp = (adv_new, -dnew, -near_obst)
        if best_cmp is None or cmp > best_cmp:
            best_cmp, best_move = cmp, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]