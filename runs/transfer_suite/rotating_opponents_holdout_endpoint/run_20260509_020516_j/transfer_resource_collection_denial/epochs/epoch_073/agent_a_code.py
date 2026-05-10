def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    center = (w - 1) / 2.0, (h - 1) / 2.0
    my_next = [(sx + dx, sy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    def cell_score(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return -10**18
        # Choose a resource where we are likely to secure first; if none, choose the best contested one.
        best = -10**18
        for rx, ry in resources:
            r = (rx, ry)
            my_d = abs(rx - nx) + abs(ry - ny)
            op_d = abs(rx - ox) + abs(ry - oy)
            lead = op_d - my_d  # positive means we get there sooner/equal disadvantage for opponent
            # Add small tie-break preference: closer to cell center to reduce dithering late.
            cx, cy = center
            center_bias = -0.03 * (abs(nx - cx) + abs(ny - cy))
            # Immediate pick incentive
            immediate = 1.0 if (rx == nx and ry == ny) else 0.0
            # If we can secure, strongly prefer; otherwise prefer to deny by reducing op's access (make lead less negative).
            score = (4.0 * lead) + (2.0 if lead >= 1 else 0.0) + immediate + center_bias
            if score > best:
                best = score
        return best

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]