def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y):
                resources.append((x, y))

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
    else:
        tx, ty = resources[0]
        best = None
        best_adv = -10**18
        center = ((W - 1) // 2, (H - 1) // 2)
        for x, y in resources:
            my_d = abs(x - sx) + abs(y - sy)
            op_d = abs(x - ox) + abs(y - oy)
            adv = op_d - my_d  # prefer resources opponent is farther from
            tie = -(abs(x - center[0]) + abs(y - center[1]))
            key = (adv, tie, -my_d, -x, -y)
            if best is None or key > best:
                best = key
                tx, ty = x, y
                best_adv = adv

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        my_dist = abs(nx - tx) + abs(ny - ty)
        op_dist = abs(nx - ox) + abs(ny - oy)
        res_bonus = 0
        if resources and (nx, ny) in set(resources):
            res_bonus = 1000
        # Objective: get closer to target, but also keep separation from opponent
        val = -my_dist + 0.35 * op_dist + res_bonus
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]