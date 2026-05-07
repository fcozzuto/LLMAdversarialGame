def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = int(observation.get("turns_remaining", 0))

    obst = set()
    for a in obstacles:
        try:
            x, y = a
            obst.add((int(x), int(y)))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    center = (w // 2, h // 2)
    opp_bias = 0.9
    time_bias = 0.15 if turns_remaining > 0 else 0.0

    best_move = (0, 0)
    best_val = -10**18

    if not resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
                continue
            val = dist(nx, ny, center[0], center[1]) * 0.6 - dist(nx, ny, ox, oy) * (1.2 - time_bias)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            continue

        best_for_cell = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            # Prefer reaching resources quickly; also prefer resources where opponent is relatively far.
            # Slightly favor moves toward center early to avoid pathing dead-ends.
            val = -my_d + opp_bias * (opp_d - my_d) * 0.5 + time_bias * (-dist(nx, ny, center[0], center[1]))
            # If resource is on our neighbor (my_d==0 implies standing on it), strongly prioritize.
            if my_d == 0:
                val += 1000
            best_for_cell = max(best_for_cell, val)

        # If multiple cell options tie, keep determinism by secondary scoring toward center and away from opponent.
        cell_score = best_for_cell - 0.05 * dist(nx, ny, center[0], center[1]) - 0.02 * dist(nx, ny, ox, oy)
        if cell_score > best_val:
            best_val = cell_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]