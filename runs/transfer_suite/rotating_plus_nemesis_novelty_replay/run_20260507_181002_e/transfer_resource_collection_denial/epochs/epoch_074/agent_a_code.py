def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tr = int(observation.get("turns_remaining", 0) or 0)
    rem_cnt = int(observation.get("remaining_resource_count", len(res)) or len(res))

    def d(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Maximize our advantage for the most swingy contestable target; add small pressure to move efficiently.
        val = -10**18
        for rx, ry in res:
            self_steps = d(nx, ny, rx, ry)
            opp_steps = d(ox, oy, rx, ry)
            # Prefer targets where we can arrive no later; amplify when opponent is close.
            advantage = (opp_steps - self_steps)
            urgency = 0
            if opp_steps <= tr // 2 + 2:
                urgency = 1
            # Encourage finishing sooner when resources are fewer.
            speed = (self_steps == 0) * 3 + (1.0 / (1 + self_steps))
            score = advantage * (1 + 0.15 * urgency) + speed - 0.01 * (rem_cnt)
            if score > val:
                val = score

        # Tie-break: closer to resources if values equal.
        if val > best_val + 1e-12:
            best_val = val
            best_move = (dx, dy)
        elif abs(val - best_val) <= 1e-12:
            if d(sx + best_move[0], sy + best_move[1], res[0][0], res[0][1]) > d(nx, ny, res[0][0], res[0][1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]