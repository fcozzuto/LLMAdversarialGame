def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2 and (p[0], p[1]) not in obstacles]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        return [0, 0]

    def clamp_dir(d):
        return -1 if d < 0 else (1 if d > 0 else 0)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Intercept target: a resource that opponent could take quickly; we try to contest it.
    # Choose deterministically the "most contested" resource by ordering.
    contested = None
    for rx, ry in res:
        do = man(ox, oy, rx, ry)
        ds = man(sx, sy, rx, ry)
        # Opponent-first resources we can reach about not much later
        score = (do - ds, -do, rx, ry)
        if contested is None or score > contested[0]:
            contested = (score, rx, ry)
    _, tx, ty = contested[0], contested[1], contested[2] if contested else (None, res[0][0], res[0][1])

    best = (None, None, None)  # (value, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        my_to_target = man(nx, ny, tx, ty)
        opp_to_target = man(ox, oy, tx, ty)

        v = 0
        # Hard reward if we land on a resource.
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds == 0:
                v += 10**7
            # Prefer states where we are closer than opponent for many resources.
            if ds < do:
                v += (do - ds) * 200 - ds
            else:
                v -= (ds - do) * 40
            # Slight bias toward ending nearer to a contested resource.
            v += -ds if (rx == tx and ry == ty) else 0

        # Additional contest pressure: reduce gap to contested target relative to opponent.
        # If opponent is already very close to the contested target, prioritize reaching it even if it costs other gains.
        v += (opp_to_target - my_to_target) * (300 if opp_to_target <= 4 else 120)

        # Deterministic tie-break: prefer moves that progress in x then y toward the contested target.
        px = clamp_dir(tx - sx)
        py = clamp_dir(ty - sy)
        v += (dx == px) * 3 + (dy == py) * 1

        if best[0] is None or v > best[0]:
            best = (v, dx, dy)

    return [best[1], best[2]] if best[0] is not None else [0, 0]