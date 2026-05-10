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

    if opp:
        opp_list = list(opp)
        tx, ty = min(opp_list, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    else:
        # No opponent cells yet: head toward center-ish unclaimed
        ulist = list(unclaimed)
        if not ulist:
            return [0, 0]
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx, ty = min(ulist, key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        in_opp = (nx, ny) in opp
        in_un = (nx, ny) in unclaimed
        in_self = (nx, ny) in selft

        adj_opp = False
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if (ax, ay) in opp:
                    adj_opp = True
        # Prefer flipping/contesting nearby opponent, otherwise expanding into unclaimed.
        score = 0
        if in_opp:
            score += 12
        if in_un:
            score += 7
        if adj_opp:
            score += 4
        if not in_self and not in_opp and not in_un:
            score -= 2  # discourage wandering

        # Distance shaping: move toward chosen target, but keep obstacle-safe.
        score += -0.8 * (abs(tx - nx) + abs(ty - ny))

        # Mild preference for not staying still if alternatives exist
        if dx == 0 and dy == 0:
            score -= 0.5

        if score > best[0]:
            best = (score, dx, dy)
        elif score == best[0]:
            # Deterministic tie-break: lexicographic dx,dy preferring larger movement toward target
            if abs(nx - tx) + abs(ny - ty) < abs(x + best[1] - tx) + abs(y + best[2] - ty):
                best = (score, dx, dy)

    return [int(best[1]), int(best[2])]