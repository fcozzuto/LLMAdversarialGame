def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Contention-aware target: prioritize resources where we are closer OR can overtake soon.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # If opponent is closer, strongly value being able to catch/deny (small sd, small od, small gap).
        gap = od - sd
        val = (gap * 60) - (sd * 6) - (rx + ry) * 0.002
        if od < sd:
            val += (sd - od) * 15 - od * 1.5
        if best is None or val > best[0] or (val == best[0] and sd < best[1]):
            best = (val, sd, rx, ry)

    _, _, tx, ty = best

    # Evaluate immediate moves by improvement toward target and reducing opponent's advantage on it.
    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    bestm = None
    for dx, dy, nx, ny in valid:
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Also softly encourage moving toward any resource we're currently behind on (deny trail).
        behind = 0
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if od < sd:
                gap = sd - od
                if gap <= 3:
                    behind += (4 - gap)
        score = (opd - myd) * 25 - myd * 2 - behind * 1.2
        if bestm is None or score > bestm[0] or (score == bestm[0] and (abs(dy) + abs(dx)) < bestm[1]):
            bestm = (score, abs(dx) + abs(dy), dx, dy)

    return [int(bestm[2]), int(bestm[3])]