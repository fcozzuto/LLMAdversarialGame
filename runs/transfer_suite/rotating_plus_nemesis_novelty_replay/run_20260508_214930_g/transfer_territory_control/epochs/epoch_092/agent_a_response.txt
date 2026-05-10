def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Prefer expanding into unclaimed cells that are adjacent to our territory (frontier).
    frontier = []
    for (x, y) in unclaimed:
        if (x, y) in obstacles:
            continue
        for ddx, ddy in dirs8:
            ax, ay = x + ddx, y + ddy
            if (ax, ay) in self_t:
                frontier.append((x, y))
                break

    # If no frontier, target any unclaimed cell.
    targets = frontier if frontier else list(unclaimed)
    # Deterministic choice of target based on nearest then a small tie-break using turn_index parity.
    parity = (observation.get("turn_index", 0) % 2)
    if targets:
        tx, ty = min(targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), (p[1] & 1) ^ parity, p[0], p[1]))
    else:
        tx, ty = ox, oy  # fallback

    best = (0, 0)
    best_score = -10**18

    # Move evaluation: pursue frontier/unclaimed, avoid stepping into opponent territory unless it helps closing distance.
    for ddx, ddy in dirs8:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        score = 0

        # Strongly reward controlling new/unclaimed.
        if (nx, ny) in self_t:
            score += 2
        if (nx, ny) in unclaimed:
            score += 25
            # Extra reward if this cell is adjacent to our territory (staying on expansion line).
            for adx, ady in dirs8:
                if (nx + adx, ny + ady) in self_t:
                    score += 18
                    break

        # If move enters opponent territory, it can flip; use this only when it reduces distance to our target.
        if (nx, ny) in opp_t:
            base = abs(tx - sx) + abs(ty - sy)
            after = abs(tx - nx) + abs(ty - ny)
            if after < base:
                score += 140
            else:
                score -= 140

        # Global guidance: reduce distance to chosen target.
        score += 60 * (abs(tx - sx) + abs(ty - sy) - (abs(tx - nx) + abs(ty - ny)))

        # Keep pressure away from opponent by avoiding getting closer unless we are also improving target distance.
        d_before = abs(sx - ox) + abs(sy - oy)
        d_after = abs(nx - ox) + abs(ny - oy)
        score += 8 * (d_before - d_after)

        # Mild preference for moves that are not purely stationary unless no options.
        score += -1 if (ddx == 0 and ddy == 0) else 0

        # Deterministic tie-break
        cand = (score, -abs(ddx) - abs(ddy), -nx, -ny)
        if cand > (best_score, -abs(best[0]) - abs(best[1]), -best[0], -best[1]):
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]