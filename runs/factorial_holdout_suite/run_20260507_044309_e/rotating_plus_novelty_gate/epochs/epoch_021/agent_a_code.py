def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx + dy
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid_targets = [(rx, ry) for (rx, ry) in resources if inb(rx, ry)]
    if not valid_targets:
        return [0, 0]

    # If we're adjacent to any resource, grab it deterministically.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        for rx, ry in valid_targets:
            if nx == rx and ny == ry:
                return [dx, dy]

    best = None; best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate contest: who arrives first, tie-break by favoring lower opponent arrival.
        cur = -10**18
        for rx, ry in valid_targets:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            if sd == 0:
                val = 10**12
            else:
                # Primary: arrival advantage
                val = (od - sd) * 10**6
                # Secondary: prefer truly winnable targets and closer ones
                if sd < od:
                    val += (od - sd) * 10**5
                elif sd == od:
                    val -= 2000
                # Tertiary: bias toward resources that are "toward opponent" to intercept
                val += (rx - ox) * 0 + (ry - oy) * 0
                # Prefer nearer resources when advantage is similar
                val -= sd * 200
            # Small deterministic bias by coordinate to break ties
            val += (rx * 3 + ry * 5) * 0.1
            if val > cur:
                cur = val
        # If movement is blocked (stay), penalize to keep progress
        if dx == 0 and dy == 0:
            cur -= 500
        if cur > best_val + 1e-9:
            best_val = cur; best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]