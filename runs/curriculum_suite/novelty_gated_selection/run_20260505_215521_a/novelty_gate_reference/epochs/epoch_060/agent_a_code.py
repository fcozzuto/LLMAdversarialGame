def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
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

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Favor resources far from opponent; also slightly prefer moving toward them.
    # If opponent is close to a resource, deprioritize it.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my = (nx, ny)
        # Evaluate best target from this move.
        move_val = -10**18
        for rx, ry in resources:
            r = (rx, ry)
            d_my = dist(my, r)
            d_opp = dist((ox, oy), r)

            # Big reward for being relatively far from opponent (steal safer items).
            # Penalty if move is far from the resource and if opponent is very close.
            val = 6.0 * d_opp - 2.2 * d_my - (1.5 if d_opp <= 2 else 0.0) - (2.5 if d_opp == 0 else 0.0)

            # Small tie-breaker for progressing outward from opponent direction.
            # Encourages interception arcs without direct chasing.
            val += 0.15 * (dist((ox, oy), r) - dist(my, (ox, oy)))

            if val > move_val:
                move_val = val

        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]