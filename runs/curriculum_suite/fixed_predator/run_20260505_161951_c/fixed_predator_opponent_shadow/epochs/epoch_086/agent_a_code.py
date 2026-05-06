def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            key = (d, -abs(nx - ox) - abs(ny - oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_move = (0, 0)
    best_val = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # Prefer a resource where we can get there sooner than opponent; penalize giving opponent priority.
        move_best = None
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # Arrival advantage; strongly penalize cases where opponent is already closer (od <= sd).
            adv = od - sd
            closer_pen = 0 if od > sd else -(1000 + sd)
            val = (closer_pen + adv, -sd, -od)
            if move_best is None or val > move_best:
                move_best = val
        if best_val is None or move_best > best_val:
            best_val = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]