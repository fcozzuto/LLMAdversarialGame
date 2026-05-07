def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        cur_best = -10**18
        # Greedy lookahead: pick the resource we are predicted to reach before the opponent.
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Big incentive to be closer than opponent; tie-break: reach sooner.
            val = (od - sd) * 100 - sd
            # Small bias away from being trapped near obstacles.
            if (nx + 1, ny) in obstacles or (nx - 1, ny) in obstacles or (nx, ny + 1) in obstacles or (nx, ny - 1) in obstacles:
                val -= 1
            if val > cur_best:
                cur_best = val
        # If we can't compute (shouldn't), skip.
        if cur_best > best_val or (cur_best == best_val and (dx, dy) < best_move):
            best_val = cur_best
            best_move = (dx, dy)

    # If all moves were blocked, stay put.
    return [int(best_move[0]), int(best_move[1])]