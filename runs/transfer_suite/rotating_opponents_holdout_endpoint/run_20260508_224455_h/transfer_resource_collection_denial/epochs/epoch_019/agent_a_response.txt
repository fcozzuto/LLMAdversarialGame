def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]
    if (sx, sy) in obstacles:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # Score is deterministic: prioritize picking a resource we can contest (self closer than opp),
    # then choose the move that maximizes advantage while reducing our distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_score = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # advantage: we want sd < od, also minimize sd and avoid letting opponent be closer than us
            adv = od - sd
            # soft pathing nudge: if resource is closer in both coords, prefer it (diagonal-friendly)
            coord_nudge = -((abs(nx - rx) + abs(ny - ry)) & 7)
            s = (adv, -sd, coord_nudge, -rx, -ry)
            if move_score is None or s > move_score:
                move_score = s
        if move_score is None:
            continue

        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]