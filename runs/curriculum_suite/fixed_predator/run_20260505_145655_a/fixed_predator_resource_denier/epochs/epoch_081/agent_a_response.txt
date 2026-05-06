def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles):
            continue

        # Score move by the best contestable resource after the move.
        # Prefer resources where opponent is close and we can arrive no later than them.
        move_val = -10**9
        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # "Denial": large when we can beat/tie opponent on a resource they threaten.
            contest = (opp_d - my_d) * 25 - my_d
            # Additional bias toward resources that are threatened (small opp_d).
            threat = (16 - opp_d) * 2
            # Tiny tie-break to reduce dithering.
            tie = -0.001 * (rx + 3 * ry)
            v = contest + threat + tie
            if v > move_val:
                move_val = v

        # If we can't contest any resource, still move toward the most threatened one.
        if move_val < -10**8:
            res = min(resources, key=lambda p: man(ox, oy, p[0], p[1]))
            move_val = -man(nx, ny, res[0], res[1])

        if best_val is None or move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]