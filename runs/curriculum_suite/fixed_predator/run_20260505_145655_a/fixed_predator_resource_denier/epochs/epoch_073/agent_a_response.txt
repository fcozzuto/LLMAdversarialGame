def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Identify opponent's current most attractive resource (resource_denier behavior)
    opp_best = None
    opp_best_d = None
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if opp_best is None or d < opp_best_d or (d == opp_best_d and (rx + ry) < (opp_best[0] + opp_best[1])):
            opp_best = (rx, ry)
            opp_best_d = d
    bx, by = opp_best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = None
    best_val = None
    for dx, dy, nx, ny in moves:
        our_d_to_opp = man(nx, ny, bx, by)
        opp_d_to_opp = opp_best_d
        # Interception pressure: beat opponent on their preferred resource
        val = (opp_d_to_opp - our_d_to_opp) * 35 - our_d_to_opp

        # Also try to secure any resource where we can be first
        best_grab = -10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # If we can race (sd <= od), reward strongly; otherwise small reward for not falling too far behind
            if sd <= od:
                g = (od - sd) * 30 - sd
            else:
                g = -sd + (od - sd) * 2
            if g > best_grab:
                best_grab = g
        val += best_grab * 0.6

        # Mild center bias to reduce stuck/oscillation
        val -= (abs(nx - cx) + abs(ny - cy)) * 0.01

        if best_val is None or val > best_val or (val == best_val and (abs(dx) + abs(dy), -dx, -dy) < (abs(best_move[0]) + abs(best_move[1]), -best_move[0], -best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]