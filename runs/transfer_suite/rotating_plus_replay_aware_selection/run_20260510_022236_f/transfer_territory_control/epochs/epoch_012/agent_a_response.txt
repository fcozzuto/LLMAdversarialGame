def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(lst):
        s = set()
        if not lst:
            return s
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells") or observation.get("unclaimed"))
    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))

    tx = ty = None
    if resources:
        tx, ty = min(resources, key=lambda p: (abs(sx - p[0]) + abs(sy - p[1]), p[0], p[1]))
    else:
        # favor unclaimed toward opponent to fight edge-claims deterministically
        ux = list(unclaimed)
        if ux:
            vx, vy = ox - sx, oy - sy
            def prog(p):
                x, y = p
                # signed projection along vector to opponent (prefer moving "forward")
                dot = (x - sx) * vx + (y - sy) * vy
                return (-dot, abs(x - ox) + abs(y - oy), x, y)
            tx, ty = min(ux, key=prog)
        else:
            tx, ty = ox, oy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            val = -1000  # discourage obstacle collisions
        else:
            val = 0
            if (nx, ny) in oppT:
                val += 6  # flipping on entry
            elif (nx, ny) in unclaimed:
                val += 4
            elif (nx, ny) in selfT:
                val += 1
            # approach target
            val += 2 * (-(abs(nx - tx) + abs(ny - ty)))
            # slightly prefer staying with safer distance from opponent unless flipping
            if (nx, ny) not in oppT:
                val += -0.25 * (abs(nx - ox) + abs(ny - oy))
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]