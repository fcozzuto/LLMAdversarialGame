def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obs = set((x, y) for x, y in obstacles)

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    def step_toward(px, py, tx, ty):
        dx = 0 if tx == px else (1 if tx > px else -1)
        dy = 0 if ty == py else (1 if ty > py else -1)
        nx, ny = px + dx, py + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return dx, dy
        # fallback: try axis moves deterministically
        cands = [(dx, 0), (0, dy), (0, 0)]
        for ddx, ddy in cands:
            nx, ny = px + ddx, py + ddy
            if inb(nx, ny) and (nx, ny) not in obs:
                return ddx, ddy
        return 0, 0

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    # Pick targets that are "contested": prioritize where we can gain (or deny) tempo.
    # Evaluate moves by how much they increase our closeness relative to the opponent.
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # If we're forced into a bad local step, penalize slightly.
        local_pen = 0.05 if (mx == 0 and my == 0) else 0.0

        # Compute best target after this move.
        best_target_score = -10**18
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)

            # lead > 0 means we are closer after the move
            lead = do - ds

            # If opponent is closer now, prefer resources where we reduce their lead most.
            # Encourage grabbing closer resources when lead is non-negative.
            dist_term = -0.6 * ds
            contest_term = 1.4 * lead if lead >= 0 else 1.0 * lead  # still matters, just less

            # Small bias toward resources not too far from center to avoid edge traps.
            cx, cy = (gw - 1) / 2.0, (gh - 1) / 2.0
            center_bias = -0.002 * ((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))

            score = contest_term + dist_term + center_bias
            # Tie-break deterministically by (rx, ry)
            if score > best_target_score or (score == best_target_score and (rx, ry) < best_target_target):
                best_target_score = score
                best_target_target = (rx, ry)

        val = best_target_score - local_pen

        if val > best_val or (val == best_val and (mx, my) < best_move):
            best_val = val
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]