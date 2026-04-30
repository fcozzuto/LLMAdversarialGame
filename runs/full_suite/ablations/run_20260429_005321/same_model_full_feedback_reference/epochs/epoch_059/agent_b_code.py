def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(a, b, c, d2):
        dx = a - c
        dy = b - d2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resset = set(resources)

    best_move = (0, 0)
    best_val = -10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Immediate pickup
        val = 0
        if (nx, ny) in resset:
            val += 10**9

        # Resource contest: prefer resources we are closer to than opponent
        if resources:
            local_best = -10**30
            for rx, ry in resources:
                my = d(nx, ny, rx, ry)
                opp = d(ox, oy, rx, ry)
                # Advantage: positive if we are closer than opponent (in squared dist space)
                adv = opp - my
                # Small tie-break to move toward nearer resources overall
                local = adv - 0.02 * my
                # If we are on top of a resource, already handled by pickup term
                if local > local_best:
                    local_best = local
            val += local_best

        # Safety: avoid stepping too near obstacles
        for ax, ay in obstacles:
            if d(nx, ny, ax, ay) == 1:
                val -= 2.0

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]