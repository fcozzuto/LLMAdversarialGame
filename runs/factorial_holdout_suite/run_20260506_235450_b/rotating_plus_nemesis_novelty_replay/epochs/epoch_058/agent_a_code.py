def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (None, None))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    res_list = []
    for r in resources:
        try:
            res_list.append((r[0], r[1]))
        except:
            pass

    def eval_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**12
        if not res_list:
            return 0

        best = -10**12
        for rx, ry in res_list:
            our_d = abs(nx - rx) + abs(ny - ry)
            if ox is None or oy is None:
                margin = -our_d
            else:
                opp_d = abs(ox - rx) + abs(oy - ry)
                # Prefer resources we can reach sooner; tie-break by smaller our distance.
                margin = (opp_d - our_d) * 4 - our_d
            # Slightly prefer moves that don't leave us worse than current
            cur_best = min(abs(sx - ax) + abs(sy - ay) for ax, ay in res_list)
            new_best = our_d
            margin += (cur_best - new_best)
            if (rx, ry) in obstacles:
                margin -= 3
            if margin > best:
                best = margin
        return best

    best_move = (0, 0)
    best_val = -10**13
    # Deterministic tie-break order: center then E,W,N,S then diagonals by listed order
    for dx, dy in moves:
        v = eval_move(dx, dy)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]