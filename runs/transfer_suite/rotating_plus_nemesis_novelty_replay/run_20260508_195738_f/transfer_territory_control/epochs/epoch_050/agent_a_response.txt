def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []
    selft = observation.get("self_territory", []) or []
    oppt = observation.get("opponent_territory", []) or []

    obs = set((p[0], p[1]) for p in obstacles)
    un = set((p[0], p[1]) for p in unclaimed)
    st = set((p[0], p[1]) for p in selft)
    ot = set((p[0], p[1]) for p in oppt)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp_count = 0
    for (px, py) in neigh8:
        if (x + px, y + py) in ot:
            opp_count += 1

    # nearest unclaimed distance for tie-breaking / pressure
    def nearest_unclaimed_dist(nx, ny):
        if not un:
            return 10**9
        md = 10**9
        for (ux, uy) in un:
            d = abs(ux - nx) + abs(uy - ny)
            if d < md:
                md = d
        return md

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0.0
        if (nx, ny) in st:
            score += 0.25
        elif (nx, ny) in un:
            score += 3.25
        elif (nx, ny) in ot:
            score += 2.25 + 0.35 * opp_count

        adj_un = 0
        adj_opp = 0
        for ax, ay in neigh8:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty):
                if (tx, ty) in un:
                    adj_un += 1
                elif (tx, ty) in ot:
                    adj_opp += 1
        score += 0.18 * adj_un
        score -= 0.10 * adj_opp

        # move toward unclaimed if available; otherwise move toward center-ish
        if un:
            score -= 0.06 * nearest_unclaimed_dist(nx, ny)
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score -= 0.02 * (abs(nx - cx) + abs(ny - cy))

        # deterministic tie-breaker: prefer staying still, then lower dx, then lower dy
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) == (0, 0) and best_move != (0, 0):
                best_move = (dx, dy)
            elif (dx, dy) != (0, 0) and best_move != (0, 0):
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]