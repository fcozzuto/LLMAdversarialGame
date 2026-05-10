def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Evaluate next step by how much closer we are to a "winnable" resource than the opponent
    best = None
    best_score = None

    tr = int(observation.get("turns_remaining", 0))
    urgency = 1.0 + (1.0 / (1.0 + tr))  # slightly favors earlier pickups

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        step_score = -10**9
        # Opponent one-step threat: resources we'd give up immediately
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # win if we can arrive no later than opponent (tie favored)
            win_margin = (od - sd)
            # discourage moves where opponent is adjacent to target while we are not
            opp_adj = 1 if od <= 1 else 0
            # prefer nearer targets when margins tie
            tie_break = -sd
            # urgency increases value for nearer wins; also penalize "losing" margins
            value = (win_margin * 10.0 * urgency) + (tie_break * 1.0) - (opp_adj * 2.0)
            if value > step_score:
                step_score = value

        if best_score is None or step_score > best_score:
            best_score = step_score
            best = (dx, dy)

    if best is None:
        return [0, 0]

    dx, dy = best
    return [int(dx), int(dy)]