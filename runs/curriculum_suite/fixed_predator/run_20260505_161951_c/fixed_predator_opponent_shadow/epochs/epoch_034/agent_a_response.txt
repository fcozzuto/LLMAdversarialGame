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

    def moves_from(x, y):
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    out.append((dx, dy, nx, ny))
        return out

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        mv = moves_from(sx, sy)
        best, bestv = (0, 0), None
        for dx, dy, nx, ny in mv:
            v = (man(nx, ny, tx, ty), man(nx, ny, ox, oy))
            if bestv is None or v < bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    mv = moves_from(sx, sy)
    cx, cy = (gw - 1) // 2, (gh - 1) // 2
    best_move = (0, 0)
    best_val = None

    # Decide targets: if opponent is closer to a resource, intercept from opponent toward it.
    targets = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if od <= sd:
            step_x = ox + (0 if rx == ox else (1 if rx > ox else -1))
            step_y = oy + (0 if ry == oy else (1 if ry > oy else -1))
            if inb(step_x, step_y) and (step_x, step_y) not in obstacles:
                targets.append((step_x, step_y, rx, ry, od - sd))
            else:
                targets.append((rx, ry, rx, ry, od - sd))
        else:
            targets.append((rx, ry, rx, ry, sd - od))

    for dx, dy, nx, ny in mv:
        # Evaluate best target for this move.
        best_for_move = None
        for tx, ty, rx, ry, margin in targets:
            self_to = man(nx, ny, tx, ty)
            opp_to_res = man(ox, oy, rx, ry)
            self_to_res = man(nx, ny, rx, ry)
            # Prefer cells that are closer to the chosen contest point,
            # while increasing the opponent's advantage at the actual resource.
            v = (self_to, self_to_res - opp_to_res, man(nx, ny, cx, cy), abs(nx - rx) + abs(ny - ry))
            if best_for_move is None or v < best_for_move:
                best_for_move = v
        if best_val is None or best_for_move < best_val:
            best_val = best_for_move
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]