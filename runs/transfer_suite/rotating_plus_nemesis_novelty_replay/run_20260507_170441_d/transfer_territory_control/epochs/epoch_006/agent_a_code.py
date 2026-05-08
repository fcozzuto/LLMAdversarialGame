def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y):
                obs_set.add((x, y))
        except:
            pass

    res = observation.get("resources", None) or []
    tgt = None
    best = 10**18
    for p in res:
        try:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y) and (x, y) not in obs_set:
                d = abs(x - sx) + abs(y - sy)
                if d < best:
                    best = d
                    tgt = (x, y)
        except:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        if tgt is not None:
            val = (abs(tgt[0] - nx) + abs(tgt[1] - ny))
            val += 0.2 * (abs(ox - nx) + abs(oy - ny))  # slight caution
        else:
            # No resources known: stay away from opponent.
            val = - (abs(ox - nx) + abs(oy - ny))
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]