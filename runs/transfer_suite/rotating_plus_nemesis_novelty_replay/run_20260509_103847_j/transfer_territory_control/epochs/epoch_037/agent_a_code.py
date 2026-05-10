def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    obs_cells = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_cells.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if opT:
        ox = sum(x for x, _ in opT) / float(len(opT))
        oy = sum(y for _, y in opT) / float(len(opT))
    else:
        ox, oy = (w - 1), (h - 1)

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_cells:
            continue

        v = 0.0
        if (nx, ny) in opT:
            v += 1000.0
        elif (nx, ny) in unT:
            v += 120.0
        elif (nx, ny) in selfT:
            v += 15.0
        else:
            v += 30.0  # likely safe unclaimed/unknown

        v += -0.8 * (abs(nx - center_x) + abs(ny - center_y))  # drift to center
        v += -0.25 * (abs(nx - ox) + abs(ny - oy))  # approach opponent territory

        # discourage stepping back onto current position loop when alternative exists
        if dx == 0 and dy == 0:
            v -= 5.0

        # deterministic tie-break: lexicographic move preference
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]

    return best