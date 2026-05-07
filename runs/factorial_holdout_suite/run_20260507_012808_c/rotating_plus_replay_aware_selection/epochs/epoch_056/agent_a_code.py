def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    res_list = [tuple(r) for r in resources]
    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        total = 0
        # Focus on a few best candidate resources to keep it fast/deterministic
        # Rank by opponent closeness (denier pressure): resources opponent could grab soon.
        ranked = []
        for rx, ry in res_list:
            do = dist(ox, oy, rx, ry)
            ranked.append((do, rx, ry))
        ranked.sort(key=lambda t: (t[0], t[1], t[2]))

        for i in range(min(5, len(ranked))):
            do, rx, ry = ranked[i]
            ds = dist(nx, ny, rx, ry)
            adv = do - ds  # positive if we arrive earlier
            # Strongly prefer guaranteed earlier grabs, but also value racing close.
            if adv > 0:
                total += 50 * adv + 10 / (ds + 1)
            else:
                # If we can't beat them, reduce attractiveness; still consider blocking races when they are near.
                total -= 20 * (-adv) + 2 / (do + 1)

        # Small nudge toward closer own completion overall to avoid dithering
        # (keeps deterministic and responsive to changes)
        dmin = min(dist(nx, ny, rx, ry) for rx, ry in res_list)
        total += 0.5 / (dmin + 1)

        if total > best_score:
            best_score = total
            best = (dx, dy)

    return [best[0], best[1]]