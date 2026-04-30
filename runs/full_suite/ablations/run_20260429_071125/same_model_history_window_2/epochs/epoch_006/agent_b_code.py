def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if resources:
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue

            # Evaluate move by maximum "lead" over opponent across all resources.
            # lead = (opp_dist - self_dist): positive means we're closer than opponent.
            best_lead = -10**9
            best_d_self = 10**9
            captured = 0
            for rx, ry in resources:
                d_self = md(nx, ny, rx, ry)
                d_opp = md(ox, oy, rx, ry)
                lead = d_opp - d_self
                if d_self == 0:
                    captured = 1
                    lead = 10**6
                if lead > best_lead or (lead == best_lead and d_self < best_d_self):
                    best_lead = lead
                    best_d_self = d_self

            # Prefer capture, then better lead, then shorter distance to nearest resource.
            # Also lightly avoid getting too close to opponent while still leading.
            d_opp_from_next = md(nx, ny, ox, oy)
            val = (captured * 10**7) + (best_lead * 100) + (-best_d_self) + (-0.01 * d_opp_from_next)
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: maximize distance from opponent, else drift to center.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_to_opp = md(nx, ny, ox, oy)
        dist_center = abs(nx - cx) + abs(ny - cy)
        key = (d_to_opp, -dist_center, -(dx == 0 and dy == 0))
        if best_key is None or key > best_key or (key == best_key and (dx, dy) < best_move):
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]