def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obst = {(p[0], p[1]) for p in obstacles}

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    if not resources:
        # drift to center if no resources
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    candidates = []
    for rx, ry in resources:
        md = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # primary: prefer resources I'm closer to; secondary: smaller my distance; tertiary: coords
        candidates.append((od - md, md, rx, ry))
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    _, _, tx, ty = candidates[0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(dx, dy)]
    for ax in [-1, 0, 1]:
        for ay in [-1, 0, 1]:
            if ax == dx and ay == dy:
                continue
            # prioritize moves that reduce distance to target
            if (ax == 0 or abs(tx - (sx + ax)) <= abs(tx - sx)) and (ay == 0 or abs(ty - (sy + ay)) <= abs(ty - sy)):
                moves.append((ax, ay))

    moves.append((0, 0))
    best = (10**9, 10**9, sx, sy, 0, 0)  # (dist, obstaclePenalty, tx, ty, dx, dy)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        # tie-break deterministically by move order (mx,my)
        key = (dist, 0, mx, my)
        if key < best[:4]:
            best = (dist, 0, mx, my, mx, my)

    return [best[4], best[5]]