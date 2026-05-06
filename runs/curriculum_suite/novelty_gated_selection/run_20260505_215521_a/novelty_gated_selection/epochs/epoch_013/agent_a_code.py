def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Target selection: prioritize resources on/near opponent's row (sweep_rows counter),
    # and secondarily the closest resource overall.
    if resources:
        opp_row = oy
        best_r = None
        best_key = None
        for rx, ry in resources:
            row_bias = abs(ry - opp_row)
            key = (row_bias, man(ox, oy, rx, ry), man(sx, sy, rx, ry), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        # Deny target: choose the resource the opponent is closest to that is also on/near its row
        deny_r = None
        deny_key = None
        for rx, ry in resources:
            row_bias = abs(ry - opp_row)
            key = (row_bias, man(ox, oy, rx, ry), rx, ry)
            if deny_key is None or key < deny_key:
                deny_key = key
                deny_r = (rx, ry)
    else:
        best_r = (sx, sy)
        deny_r = (sx, sy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Progress to own target
        d_me = man(nx, ny, best_r[0], best_r[1])
        d_me_now = man(sx, sy, best_r[0], best_r[1])
        gain_me = d_me_now - d_me

        # Denial: move to reduce opponent access to deny target (increase their distance)
        d_opp = man(ox, oy, deny_r[0], deny_r[1])
        d_opp_from_my = man(nx, ny, deny_r[0], deny_r[1])
        # If I'm closer to the deny resource than the opponent is, it's a strong block.
        block = 0
        if d_opp_from_my <= d_opp:
            block = 6 - d_opp_from_my

        # Row-convergence: encourage being on/near the opponent's row (intercept sweep paths)
        row_conv = -abs(ny - oy)

        # Slight preference to keep moving toward center to avoid corner traps
        center_pref = -(abs((nx - (w - 1) / 2)) + abs((ny - (h - 1) / 2))) * 0.01

        score = (gain_me * 2.0) + block + (row_conv * 0.5) + center_pref

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]