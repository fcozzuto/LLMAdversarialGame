def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick a target resource we can reach earlier than the opponent; otherwise still prefer relative advantage.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        opp_next_d = cheb(nx, ny, ox, oy)
        my_next_d = 0
        # Evaluate move by best potential target.
        move_val = -3.0 * opp_next_d
        if resources:
            for (rx, ry) in resources:
                my_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                rel = opp_d - my_d  # positive means we are closer after this move
                # Encourage taking closest contested resources, but also progress if uncontested.
                val = 10.0 * rel - 0.8 * my_d
                if val > my_next_d:
                    my_next_d = val
            move_val += my_next_d
        else:
            # No visible resources: move away from opponent while staying central-ish.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_d = abs(nx - cx) + abs(ny - cy)
            move_val += 0.05 * center_d
        if move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]

    return best_move