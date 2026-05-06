def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    # Predict opponent's best next step toward its nearest resource (greedy nearest-resource behavior)
    opp_target = None
    opp_bestd = None
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if opp_bestd is None or d < opp_bestd:
            opp_bestd = d
            opp_target = (rx, ry)

    prx, pry = opp_target
    opp_legal = []
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if inside(nx, ny):
            opp_legal.append((dx, dy))
    # If stuck, opponent stays
    if not opp_legal:
        predicted_opp = (ox, oy)
    else:
        best = None
        best_key = None
        for dx, dy in opp_legal:
            nx, ny = ox + dx, oy + dy
            d = man(nx, ny, prx, pry)
            # Tie-break toward staying closer to our current position to avoid easy flips
            k = (d, man(nx, ny, sx, sy))
            if best_key is None or k < best_key:
                best_key = k
                best = (dx, dy)
        predicted_opp = (ox + best[0], oy + best[1])

    px, py = predicted_opp

    # Choose our move to gain relative distance advantage to that target,
    # with secondary drive to reduce our distance to the target and avoid letting opponent get closer.
    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        our_d = man(nx, ny, prx, pry)
        opp_d = man(px, py, prx, pry)
        # Higher is better: prefer making (opp_d - our_d) large; also avoid moves that increase our distance
        # and slightly favor moving toward the center to reduce getting trapped.
        center_bias = -man(nx, ny, (w - 1) // 2, (h - 1) // 2) * 0.01
        score = (opp_d - our_d) * 1000 - our_d + center_bias
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]