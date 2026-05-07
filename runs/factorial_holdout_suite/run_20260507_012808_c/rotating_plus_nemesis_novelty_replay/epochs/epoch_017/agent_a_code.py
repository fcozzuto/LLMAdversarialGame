def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        # fallback: head toward opponent to force contest, else stay
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Choose resource by who arrives first; reward closeness, punish opponent stealing.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        my_d = [abs(nx - rx) + abs(ny - ry) for rx, ry in resources]
        op_d = [abs(ox - rx) + abs(oy - ry) for rx, ry in resources]

        # Evaluate best attainable resource from this move
        val = -10**9
        for i in range(len(resources)):
            md = my_d[i]
            od = op_d[i]
            # If I can get it sooner, big reward; if opponent can, reduce strongly.
            steal_pen = 5.0 if od <= md else 0.0
            val_i = (20.0 / (1.0 + md)) - (5.0 / (1.0 + od)) - steal_pen
            # Small tie-break toward resources nearer to me and farther from opponent
            val_i += 0.02 * (od - md)
            if val_i > val:
                val = val_i

        # Mild center preference to avoid corner-lock if no clear target
        center_pref = -0.001 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        val += center_pref

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]