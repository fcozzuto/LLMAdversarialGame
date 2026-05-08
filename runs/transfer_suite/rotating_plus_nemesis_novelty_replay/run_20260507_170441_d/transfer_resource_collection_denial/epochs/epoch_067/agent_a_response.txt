def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    # Find whether there are "contested" resources close enough that we can swing the race now.
    contested = []
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        if op_d <= my_d + 1:
            contested.append((rx, ry, my_d, op_d))
    target_pool = contested if contested else [(rx, ry, dist8(sx, sy, rx, ry), dist8(ox, oy, rx, ry)) for (rx, ry) in resources]

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Bonus for distancing from opponent (helps prevent them from reaching contested first)
        opp_gain = dist8(nx, ny, ox, oy) - dist8(sx, sy, ox, oy)

        # Evaluate best resource this move would target
        move_best = None
        for rx, ry, _, _ in target_pool:
            my_d2 = dist8(nx, ny, rx, ry)
            op_d2 = dist8(ox, oy, rx, ry)

            # Core: prefer resources where our advantage improves (arrive first).
            # If we can be first, reward strongly; if not, discourage.
            adv = op_d2 - my_d2
            val = 0
            if adv >= 0:
                val += 120 + 30 * adv
            else:
                val += -70 + 10 * adv  # adv negative reduces value

            # Secondary: prefer nearer targets once raced.
            val += -2 * my_d2

            # Small preference to move toward the resource rather than orbiting
            val += 0.5 * (dist8(sx, sy, rx, ry) - my_d2)

            if move_best is None or val > move_best:
                move_best = val

        # Blend with opponent distancing to reduce immediate stealing risk
        total = move_best + 8 * opp_gain

        if best_val is None or total > best_val:
            best_val = total
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best