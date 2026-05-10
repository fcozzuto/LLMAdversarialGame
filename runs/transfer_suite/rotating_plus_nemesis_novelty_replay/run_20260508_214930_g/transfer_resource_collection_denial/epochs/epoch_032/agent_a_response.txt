def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    resset = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                resset.append((x, y))
    if not resset:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = None

    # As turns run out, prioritize reaching any resource over racing too much.
    hurry = 0.5 + (1.0 - min(1.0, float(turns_remaining) / 12.0)) * 2.0

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine keeps us in place; mimic safely

        my_best = None
        # Evaluate the best resource "claim" from the next position.
        for rx, ry in resset:
            myd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)
            margin = oppd - myd  # positive => we get there first
            center = abs(rx - cx) + abs(ry - cy)
            # Greedy race when early; value still favors smaller myd when late.
            val = (margin * (6.0 + hurry)) - (myd * (1.5 + hurry * 0.8)) - (center * 0.03)
            if my_best is None or val > my_best:
                my_best = val

        if my_best is None:
            continue
        if best_val is None or my_best > best_val:
            best_val = my_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]