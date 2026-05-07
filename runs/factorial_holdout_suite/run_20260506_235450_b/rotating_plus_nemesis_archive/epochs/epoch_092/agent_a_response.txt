def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (-(10**18), 10**9, 0, 0)  # (primary, secondary, dx, dy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        best_primary = -(10**18)
        best_secondary = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # primary: prefer resources where we are closer than opponent; break ties by smaller self distance
            primary = od - sd
            secondary = sd
            if primary > best_primary or (primary == best_primary and secondary < best_secondary):
                best_primary, best_secondary = primary, secondary

        # secondary move preference: avoid stepping farther from our currently best target-ish
        # use distance to the closest resource from current position as a small tiebreaker
        cur_min = 10**9
        for rx, ry in resources:
            d = man(sx, sy, rx, ry)
            if d < cur_min:
                cur_min = d
        new_min_est = best_secondary
        step_tiebreak = new_min_est - cur_min

        if best_primary > best_move[0] or (best_primary == best_move[0] and (best_secondary < best_move[1] or (best_secondary == best_move[1] and step_tiebreak < best_move[2]))):
            best_move = (best_primary, best_secondary, step_tiebreak, 0)
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]