def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Predict opponent's likely next target: their nearest resource.
    opp_target = min(resources, key=lambda t: (md(ox, oy, t[0], t[1]), t[0], t[1]))

    # Move options (stay included)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        # Primary objective: contest the predicted target (get closer than opponent, or reduce their lead).
        d_us = md(nx, ny, opp_target[0], opp_target[1])
        d_op = md(ox, oy, opp_target[0], opp_target[1])
        contest = d_us - d_op

        # Secondary: keep near some resource (avoid getting stuck chasing a stale target).
        d_near_us = min(md(nx, ny, rx, ry) for rx, ry in resources)

        # Tertiary: slightly favor moves that increase our distance from opponent to avoid direct swaps.
        opp_sep = md(nx, ny, ox, oy)

        key = (contest, d_near_us, -opp_sep, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]