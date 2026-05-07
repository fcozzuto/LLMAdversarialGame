def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = (0, 0)
    best_val = 10**9

    if not resources:
        # No resources visible: move toward opponent (deny path) deterministically
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = man(nx, ny, ox, oy)
                if v < best_val:
                    best_val = v
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate best resource to target from this next cell.
        # Heavily penalize resources where opponent is closer.
        mv = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            diff = myd - opd  # negative => we are closer
            penalty = 0
            if diff > 0:
                penalty = 3 * diff  # opponent can reach first: don't chase unless necessary
            # Slight preference to nearer contested resources
            v = myd + penalty
            if v < mv:
                mv = v
        # Secondary tie-break: prefer moves that keep us competitive against opponent overall
        # (closer to opponent => better blocking potential for denier).
        mv2 = mv + 0.01 * man(nx, ny, ox, oy)
        if mv2 < best_val:
            best_val = mv2
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]