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

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d1 = man(nx, ny, tx, ty)
            d2 = man(nx, ny, ox, oy)
            key = (d1, d2)
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    # Score each move by the best resource it can "gain" (prefer self to be closer than opponent)
    best_move = (0, 0)
    best_val = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_r = None
        best_r_val = None
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # primary: maximize (opp_d - self_d), secondary: smaller self_d, tertiary: closer to opponent (pressure)
            gain = opp_d - self_d
            key = (gain, -self_d, -man(nx, ny, ox, oy), -rx - ry)
            if best_r_val is None or key > best_r_val:
                best_r_val = key
                best_r = (rx, ry)
        # Encourage progressing toward whichever resource gives best gain
        if best_r is None:
            continue
        rx, ry = best_r
        self_d = man(nx, ny, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        val = (opp_d - self_d, -self_d, -man(nx, ny, ox, oy), dx == 0 and dy == 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]