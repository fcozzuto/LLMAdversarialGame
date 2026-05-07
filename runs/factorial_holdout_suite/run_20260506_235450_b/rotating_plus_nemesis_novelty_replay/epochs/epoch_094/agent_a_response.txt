def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # No resources: drift to center while avoiding obstacles.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                score = -(abs(nx - cx) + abs(ny - cy))
                if score > best_score:
                    best_score = score
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose move by evaluating best reachable resource next-step with opponent-aware scoring.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_step_d = abs(nx - sx) + abs(ny - sy)  # mostly 1 or 0
        step_best = -10**18
        for tx, ty in resources:
            my_d = abs(tx - nx) + abs(ty - ny)
            if opp_exists:
                opp_d = abs(tx - ox) + abs(ty - oy)
                # If we are closer, prioritize reaching quickly; if not, deny by increasing opp advantage.
                if my_d <= opp_d:
                    val = (opp_d - my_d) * 2 - my_d
                else:
                    val = (opp_d - my_d) * 3 - my_d * 0.5
            else:
                val = -my_d
            # Prefer grabbing a resource immediately.
            if my_d == 0:
                val += 1e6
            step_best = max(step_best, val)
        # Slight tie-break: prefer moves that reduce average distance to all resources.
        if step_best > best_score:
            best_score = step_best - my_step_d * 0.01
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]