def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, drift to center while avoiding obstacles
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = abs(nx - cx) + abs(ny - cy)
            if v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Robust greedy: prefer moves that make you "win" contests on resources
    best_move = [0, 0]
    best_val = -10**18
    cx, cy = (w - 1) // 2, (h - 1) // 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # local safety: avoid moving adjacent to obstacles (softly)
        obs_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    obs_pen += 1

        # Evaluate best contested/winnable resource from this next cell
        score = -0.15 * (abs(nx - cx) + abs(ny - cy)) - 0.5 * obs_pen
        for rx, ry in resources:
            md = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # prefer where you are closer than opponent; reward clear wins
            contest = (od - md)
            # also keep some pressure for overall proximity
            val = 2.2 * contest - 0.05 * md
            if contest >= 1:
                val += 1.0
            score += val

        if score > best_val:
            best_val = score
            best_move = [dx, dy]

    # If all moves were blocked (unlikely), stay
    return best_move