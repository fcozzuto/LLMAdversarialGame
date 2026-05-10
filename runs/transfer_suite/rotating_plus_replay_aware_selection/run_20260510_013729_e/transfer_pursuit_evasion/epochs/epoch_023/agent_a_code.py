def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role)
    is_evader = ("evad" in role) or ("runner" in role)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in ob:
                m += 1
        return m

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in ob:
            continue
        d = man(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        cen = -man(nx, ny, int(cx), int(cy))  # closer to center => larger
        if is_pursuer:
            val = (-d, -mob, -cen, dx, dy)
        elif is_evader:
            val = (d, mob, cen, -dx, -dy)
        else:
            # default: if uncertain, try to both reduce distance and keep mobility high
            val = (-d, -mob, -cen, dx, dy)

        if best_val is None or val > best_val if not is_pursuer else val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]