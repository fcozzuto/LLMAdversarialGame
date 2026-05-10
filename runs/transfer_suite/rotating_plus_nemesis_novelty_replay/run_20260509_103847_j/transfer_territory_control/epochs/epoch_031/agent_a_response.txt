def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Prefer: capture unclaimed; flip opponent territory; keep toward center; avoid obstacles.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        score = 0.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        score += (-0.35) * dist_center

        if (nx, ny) in opT:
            score += 7.5
        elif (nx, ny) in unT:
            score += 2.5
        elif (nx, ny) in selfT:
            score += 0.2
        else:
            score += 0.0

        # Extra pull toward nearest useful target to create progress deterministically.
        targets = unT if unT else opT
        if targets:
            bestd = 10**9
            for tx, ty in targets:
                d = abs(tx - nx) + abs(ty - ny)
                if d < bestd:
                    bestd = d
            score += (-0.15) * bestd

        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = cand[0]
    return [int(dx), int(dy)]