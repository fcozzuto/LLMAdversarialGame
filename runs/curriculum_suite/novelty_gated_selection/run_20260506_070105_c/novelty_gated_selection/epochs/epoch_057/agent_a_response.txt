def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) not in obstacles:
            resources.append((rx, ry))

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If no resources, move toward opponent but avoid obstacles
    if not resources:
        tx, ty = ox, oy
        best = None
        for dx, dy in deltas:
            nx, ny = clamp(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            # also avoid stepping next to obstacles if possible
            nb = 0
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0: 
                        continue
                    if (nx + ddx, ny + ddy) in obstacles:
                        nb += 1
            score = -cheb((nx, ny), (tx, ty)) - nb * 0.2
            if best is None or score > best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [int(best[1]), int(best[2])]

    # Evaluate each immediate move by best reachable target score from the next position
    best_move = (None, 0, 0)
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue

        # obstacle proximity penalty
        nb = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (nx + ddx, ny + ddy) in obstacles:
                    nb += 1

        my_next = (nx, ny)
        # choose target that I can secure (or at least contest) and not too late
        best_sc = None
        for rx, ry in resources:
            my_d = cheb(my_next, (rx, ry))
            opp_d = cheb((ox, oy), (rx, ry))
            # prefer resources where I arrive no later than opponent; bias toward quick finish
            contest = opp_d - my_d  # positive means I arrive earlier
            align = abs((rx - nx) - (ry - ny))  # slight preference for smoother diagonal progress
            sc = contest * 5.0 - my_d * 1.2 - align * 0.05
            # discourage chasing what opponent is guaranteed to reach sooner
            if contest < 0:
                sc -= (-contest) * 2.0
            if best_sc is None or sc > best_sc:
                best_sc = sc

        total = best_sc - nb * 0.25
        if best_move[0] is None or total > best_move[0]:
            best_move = (total, dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]