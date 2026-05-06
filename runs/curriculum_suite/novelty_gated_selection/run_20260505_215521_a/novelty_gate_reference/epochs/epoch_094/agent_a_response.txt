def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If opponent is very close, prioritize contesting them.
    opp_close = man(sx, sy, ox, oy) <= 3

    best_score = -10**18
    best = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dist_me_opp = man(nx, ny, ox, oy)
        if opp_close:
            score = -dist_me_opp
            if score > best_score:
                best_score = score
                best = (dx, dy)
            continue

        # Contest the most steal-prone resource: where opponent is closer than we are.
        best_res_score = -10**18
        for rx, ry in resources:
            dm = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Favor reducing our distance to that resource while penalizing letting opponent keep the lead.
            lead = do - dm  # positive => we are not behind
            # Also avoid going too far from the agent while contesting.
            s = (-dm) + 0.35 * do - 0.08 * dist_me_opp + 0.25 * lead
            if s > best_res_score:
                best_res_score = s

        # Additionally, keep pressure by preferring moves that slightly shrink contested distance to the nearest resource.
        score = best_res_score
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]