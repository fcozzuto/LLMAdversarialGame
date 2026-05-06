def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cur_opp_d = man(sx, sy, ox, oy)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy, nx, ny in moves:
            d_mid = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ox, oy)
            key = (d_mid, -d_opp, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = None
    best_tie = None

    for dx, dy, nx, ny in moves:
        self_d_to_best = None
        val = None
        for rx, ry in resources:
            self_t = man(nx, ny, rx, ry)
            opp_t = man(ox, oy, rx, ry)
            # assume opponent can also advance 1 step this turn
            opp_t_eff = opp_t - 1
            advantage = opp_t_eff - self_t
            score = advantage * 10 - self_t
            if val is None or score > val:
                val = score
                self_d_to_best = self_t

        opp_d = man(nx, ny, ox, oy)
        closer_pen = max(0, cur_opp_d - opp_d)  # discourage moving toward opponent
        val2 = val - closer_pen

        tie = (self_d_to_best, man(nx, ny, ox, oy), dx, dy)
        if best_val is None or val2 > best_val or (val2 == best_val and tie < best_tie):
            best_val = val2
            best_tie = tie
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]