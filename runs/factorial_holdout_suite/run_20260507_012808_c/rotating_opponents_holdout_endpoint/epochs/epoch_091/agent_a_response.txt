def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # From the move result, pick the resource that maximizes "we beat opponent".
        best_for_this_move = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # If we're closer, value is positive; otherwise negative. Bias toward closer races.
            val = (od - sd) * 100 - sd
            if val > best_for_this_move:
                best_for_this_move = val

        # Deterministic tie-break: prefer diagonal, then horizontal, then vertical, then stay.
        key = (-(dx != 0 and dy != 0), -(abs(dx) == 1 and dy == 0), -(abs(dy) == 1 and dx == 0), -(dx == 0 and dy == 0))
        cur = (best_for_this_move, key)
        prev = (best_val, (-(best_move[0] != 0 and best_move[1] != 0),
                               -(abs(best_move[0]) == 1 and best_move[1] == 0),
                               -(abs(best_move[1]) == 1 and best_move[0] == 0),
                               -(best_move[0] == 0 and best_move[1] == 0)))
        if cur > prev:
            best_val = best_for_this_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]