def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        best = None
        best_tuple = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            best_r = None
            best_r_val = None
            for rx, ry in resources:
                self_d = md(nx, ny, rx, ry)
                opp_d = md(ox, oy, rx, ry)
                val = (opp_d - self_d, -self_d)  # prioritize being closer than opponent
                if best_r_val is None or val > best_r_val:
                    best_r_val = val
                    best_r = (rx, ry)
            # secondary tie-breakers: move that most improves relative to opponent for the chosen resource
            rx, ry = best_r
            cur_self_d = md(sx, sy, rx, ry)
            cur_opp_d = md(ox, oy, rx, ry)
            new_self_d = md(nx, ny, rx, ry)
            rel_improve = (cur_opp_d - cur_self_d) - (cur_opp_d - new_self_d)
            t = (best_r_val[0], best_r_val[1], rel_improve, -new_self_d, dx, dy)
            if best_tuple is None or t > best_tuple:
                best_tuple = t
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: move toward the center line between agents, staying collision-safe
    tx = (sx + ox) // 2
    ty = (sy + oy) // 2
    best = None
    best_d = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d = md(nx, ny, tx, ty)
        t = (d, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_d is None or t < best_d:
            best_d = t
            best = (dx, dy)
    return [best[0], best[1]]