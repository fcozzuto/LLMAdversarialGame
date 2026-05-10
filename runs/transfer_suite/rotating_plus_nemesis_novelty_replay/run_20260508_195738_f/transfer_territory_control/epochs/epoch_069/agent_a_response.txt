def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    x0, y0 = x, y

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    opp_list = list(opp)
    if not opp_list:
        # No opponent territory known: push toward nearest unclaimed if any.
        targets = list(unclaimed)
        if not targets:
            return [0, 0]
        tx, ty = min(targets, key=lambda p: (abs(p[0] - x0) + abs(p[1] - y0), p[0], p[1]))
        dx = 0 if tx == x0 else (1 if tx > x0 else -1)
        dy = 0 if ty == y0 else (1 if ty > y0 else -1)
        return [dx, dy]

    def man(nx, ny, px, py):
        return abs(px - nx) + abs(py - ny)

    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = x0 + dx, y0 + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        # Heuristic: maximize chance to flip (entering opponent cell) and approach frontier.
        enter_opp = 1 if (nx, ny) in opp else 0
        adj_opp = 0
        if not enter_opp:
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0:
                        continue
                    ax, ay = nx + adx, ny + ady
                    if inb(ax, ay) and (ax, ay) in opp:
                        adj_opp = 1
                        break
                if adj_opp:
                    break

        # Distance to opponent territory (frontier pressure)
        nearest_opp = min(man(nx, ny, px, py) for (px, py) in opp_list)

        # Prefer unclaimed if not entering/adjacent to opponent
        on_unclaimed = 1 if (nx, ny) in unclaimed else 0
        self_owned = 1 if (nx, ny) in selft else 0

        score = 0
        score += 100000 if enter_opp else 0
        score += 5000 if adj_opp else 0
        score += -50 * nearest_opp
        score += 40 * on_unclaimed
        score += 5 * self_owned
        score += -(abs(nx - x0) + abs(ny - y0)) * 0.1  # slight preference to stay stable

        if best is None or score > best or (score == best and (dx, dy) < tuple(best_move)):
            best = score
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]