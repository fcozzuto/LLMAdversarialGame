def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if inb(x, y) and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        tx, ty = w // 2, h // 2
    else:
        def man(ax, ay, bx, by):
            dx = ax - bx
            if dx < 0: dx = -dx
            dy = ay - by
            if dy < 0: dy = -dy
            return dx + dy

        tr = int(observation.get("turns_remaining", 0))
        rem = int(observation.get("remaining_resource_count", len(valid)) or len(valid))
        few = (tr <= 6) or (rem <= 3)

        best = None
        best_key = None
        for rx, ry in valid:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd == 0:
                key = (0, -10**6)
            else:
                margin = od - sd  # positive means we arrive sooner
                adj_obs = 0
                if (rx+1, ry) in obstacles or (rx-1, ry) in obstacles or (rx, ry+1) in obstacles or (rx, ry-1) in obstacles:
                    adj_obs = 1
                # prioritize winning grabs, then safe/fast
                key = (
                    -margin,                         # maximize margin
                    sd + adj_obs * (2 if few else 1), # minimize our distance; avoid tight spots
                    abs(sx - rx) + abs(sy - ry)       # small extra tie-break
                )
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) not in obstacles:
        return [dx, dy]

    # fallback: try axis moves deterministically
    candidates = [(dx, 0), (0, dy), (dx, dy), (-dx, 0), (0, -dy), (0, 0)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [cdx, cdy]
    return [0, 0]