def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        # move toward center-ish to avoid getting stuck
        tx, ty = (w // 2), (h // 2)
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Determine the "contested" advantage: prefer moves that reduce our distance
    # to the resource more than the opponent's distance does.
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue

        my_nearest = 10**9
        my_to_res = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < my_nearest:
                my_nearest = d
                my_to_res = (rx, ry)

        if my_to_res is None:
            continue

        rx, ry = my_to_res
        my_d = my_nearest
        op_d = cheb(ox, oy, rx, ry)

        # Core score: maximize (op_d - my_d) and secondarily minimize my_d.
        # Add a small tie-break toward moving closer to where resources cluster.
        center_bias = cheb(nx, ny, w - 1, h - 1) if (sx + sy) % 2 == 0 else cheb(nx, ny, 0, 0)
        val = (op_d - my_d) * 100 - my_d - center_bias * 0.01

        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]