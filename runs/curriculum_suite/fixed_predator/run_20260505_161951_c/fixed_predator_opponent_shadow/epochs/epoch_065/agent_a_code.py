def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    # If no resources, drift toward center between agents
    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy))
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    def opp_best_step_to(cellx, celly):
        # deterministic "shadow" prediction: pick move for opponent that minimizes distance to cell
        best_d = None
        best_step = (0, 0)
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                px, py = ox + ddx, oy + ddy
                if not inb(px, py) or (px, py) in obstacles:
                    continue
                d = abs(px - cellx) + abs(py - celly)
                if best_d is None or d < best_d:
                    best_d = d
                    best_step = (ddx, ddy)
        return best_step

    best_move = (0, 0)
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy

        # evaluate this move by the best contested resource after we step
        best_resource_score = None
        best_resource_tiebreak = None
        for rx, ry in resources:
            our_d = abs(nx - rx) + abs(ny - ry)
            ddx, ddy = opp_best_step_to(rx, ry)
            px, py = ox + ddx, oy + ddy
            opp_d_next = abs(px - rx) + abs(py - ry)

            # prioritize: advantage (opp_d_next - our_d), then closeness
            adv = opp_d_next - our_d
            key_adv = (-adv, our_d)  # smaller is better: higher advantage, then closer
            if best_resource_score is None or key_adv < best_resource_tiebreak:
                best_resource_tiebreak = key_adv
                best_resource_score = adv

        # also discourage stepping into dead ends near obstacles by slight penalty
        obstacle_near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                cx, cy = nx + ax, ny + ay
                if inb(cx, cy) and (cx, cy) in obstacles:
                    obstacle_near += 1

        move_key = (best_resource_tiebreak[0], best_resource_tiebreak[1], obstacle_near, abs(nx - ox) + abs(ny - oy))
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]