def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obstacle_pen(x, y):
        if (x, y) in occ:
            return 10**9
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in occ:
                    pen += 6 if ax == 0 or ay == 0 else 4
        return pen

    def approx_dist(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        # Cheaper than sqrt; matches 8-dir behavior
        adx = dx if dx >= 0 else -dx
        ady = dy if dy >= 0 else -dy
        return (adx + ady) - min(adx, ady)  # L1-L∞ blend

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        pen = obstacle_pen(nx, ny)
        if pen >= 10**8:
            continue

        # For each resource, estimate advantage if we aim to reach it next.
        # Higher is better: prefer resources we can reach sooner than opponent.
        best_for_move = -10**18
        for rx, ry in resources:
            sd = approx_dist(nx, ny, rx, ry)
            od = approx_dist(ox, oy, rx, ry)
            # Prefer taking closer/earlier resources; strongly penalize losing races.
            adv = (od - sd)
            # Also encourage selecting a resource that's not too far away.
            score = adv * 10 - sd * 2
            # Small tie-break toward resources closer to the center of our map (midgame stability).
            mx, my = (w - 1) / 2.0, (h - 1) / 2.0
            dc = abs(rx - mx) + abs(ry - my)
            score -= int(dc * 0.1)
            if score > best_for_move:
                best_for_move = score

        # If we're directly on a resource, take it aggressively.
        if (nx, ny) in {(p[0], p[1]) for p in resources}:
            best_for_move += 200

        total = best_for_move - pen * 3
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]