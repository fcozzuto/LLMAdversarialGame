def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj_obs = set()
    for (x, y) in obstacles:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    adj_obs.add((nx, ny))

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    has_res = len(resources) > 0
    res_list = resources if has_res else [((w - 1 - ox), (h - 1 - oy))]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # evaluate best target reachable from this next state, favoring resources where we gain relative advantage
        # and avoiding getting too close to obstacles.
        obs_pen = 18 if (nx, ny) in adj_obs else 0
        cur_best = -10**18

        for tx, ty in res_list:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Higher is better: lower ds, higher (do - ds), small preference for nearer targets
            val = (do - ds) * 120 - ds * 6
            # If landing adjacent to opponent, slightly discourage unless resource is also very close
            adv_op = cheb(nx, ny, ox, oy)
            if adv_op == 1:
                val -= 25 if ds > 1 else 0
            # Strongly encourage going directly onto a resource
            if (nx, ny) == (tx, ty):
                val += 10000
            if val > cur_best:
                cur_best = val

        total = cur_best - obs_pen
        # Deterministic tie-break: prefer moves with smallest dx,dy lex order after maximizing
        if total > best_val or (total == best_val and (dx, dy) < best_move):
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]