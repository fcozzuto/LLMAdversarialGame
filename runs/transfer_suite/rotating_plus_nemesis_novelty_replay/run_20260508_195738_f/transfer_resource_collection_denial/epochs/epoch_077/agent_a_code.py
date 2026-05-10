def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    opp_same_row = (oy == sy)
    opp_same_col = (ox == sx)

    best_move = [0, 0]
    best_score = -1e18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # "Interception" objective: maximize advantage against the nearest contested resource.
        # Score = best (opp_dist - self_dist) over resources, plus small distance-to-target bias.
        best_adv = -1e9
        best_selfd = 1e9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_selfd):
                best_adv = adv
                best_selfd = sd

        # Anti-sweep-row bias: if opponent is aligned, avoid continuing straight into their sweep lanes.
        sweep_pen = 0.0
        if opp_same_row and dy == 0:
            # discourage staying on the same row when opponent could sweep it
            # stronger if there are resources on that row near us
            row_near = 0
            for rx, ry in resources:
                if ry == sy:
                    row_near += 1
            sweep_pen = 0.6 * (1 + row_near)

        if opp_same_col and dx == 0:
            col_near = 0
            for rx, ry in resources:
                if rx == sx:
                    col_near += 1
            sweep_pen = max(sweep_pen, 0.6 * (1 + col_near))

        # Keep distance if we'd end up too close to opponent (prevents being herded)
        adj = cheb(nx, ny, ox, oy)
        herd_pen = 0.0
        if adj <= 1:
            herd_pen = 0.8 * (2 - adj)

        # Tie-break: prefer moves that actually reduce distance to some resource
        score = (2.2 * best_adv) - (0.05 * best_selfd) - sweep_pen - herd_pen
        if score > best_score or (score == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move