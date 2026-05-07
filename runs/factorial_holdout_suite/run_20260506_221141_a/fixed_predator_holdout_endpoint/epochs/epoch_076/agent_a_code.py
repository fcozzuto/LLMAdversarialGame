def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources_sorted = sorted(resources, key=lambda p: (p[0], p[1]))

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose a move that secures resources against denial:
        # For each candidate resource, measure how much closer we are than opponent,
        # with a bias toward sooner collection.
        local_best = None
        for tx, ty in resources_sorted:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            if od < sd:
                # Opponent is closer; still allow if we can snatch quickly.
                val = (od - sd) - 0.15 * sd
            else:
                val = (od - sd) + 0.15 * (1.0 / (1 + sd))
            # Also prefer nearer resources if tie in denial margin
            val = (val, -sd)
            if local_best is None or val > local_best:
                local_best = val

        if best_val is None or local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]