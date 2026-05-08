def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -(abs(nx - tx) + abs(ny - ty)) + 0.05 * (abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        total = 0
        min_my = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            md = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            if md < min_my:
                min_my = md
            if od < min_opp:
                min_opp = od
            # Prefer resources where we are closer than opponent; also prefer closeness overall.
            # Strongly reward immediate picks (md==0).
            if md == 0:
                v = 1e9 + 1000
            else:
                lead = od - md  # positive if we are closer
                v = 100 * lead - 2 * md
                # If opponent is extremely close, downweight to reduce chasing
                if od <= 1 and md > od:
                    v -= 30
            total += v

        # Small tiebreak: move that reduces our nearest distance; and avoids letting opponent get a clear win.
        v = total + (-5 * min_my) + (1 * (min_opp - min_my))
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best