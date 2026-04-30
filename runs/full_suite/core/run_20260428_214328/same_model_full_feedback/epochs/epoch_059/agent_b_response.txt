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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best_move = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            # Evaluate best target for this move
            move_val = -10**18
            for rx, ry in resources:
                d_us = man(nx, ny, rx, ry)
                d_op = man(ox, oy, rx, ry)
                # Prioritize targets we can reach sooner than opponent; also prefer closer targets.
                # Big weight on (d_op - d_us) to "steal" targets.
                v = (d_op - d_us) * 10 - d_us
                if v > move_val:
                    move_val = v
            # small preference for moves that reduce our distance to the set of resources
            # (stabilizes against tie oscillations)
            nearest = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < nearest:
                    nearest = d
            move_val = move_val - nearest * 0.05
            if move_val > best_val:
                best_val = move_val
                best_move = (dx, dy)
            elif move_val == best_val:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)
    else:
        # No visible resources: move to intercept/close while avoiding obstacles
        cx, cy = w // 2, h // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_op_next = man(nx, ny, ox, oy)
            d_center = man(nx, ny, cx, cy)
            # chase opponent but lightly keep centered
            v = -d_op_next * 10 - d_center
            if v > best_val:
                best_val = v
                best_move = (dx, dy)
            elif v == best_val:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]