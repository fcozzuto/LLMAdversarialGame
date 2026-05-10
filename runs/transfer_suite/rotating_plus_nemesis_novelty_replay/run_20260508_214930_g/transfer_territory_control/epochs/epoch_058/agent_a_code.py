def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (7, 7))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    manh_opp = abs(sx - ox) + abs(sy - oy)

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def local_unclaimed_count(x, y):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                c += 1
        return c

    best = [0, 0]
    best_score = -10**18
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0

        if (nx, ny) in unclaimed:
            score += 120
        if (nx, ny) in self_t:
            score += 18
        if (nx, ny) in opp_t:
            score -= 60

        # Prefer expanding into unclaimed "fronts"
        score += local_unclaimed_count(nx, ny) * 12

        # Maintain pressure while not overcommitting into opponent territory
        d_before = manh_opp
        d_after = abs(nx - ox) + abs(ny - oy)
        score += (d_before - d_after) * 6

        # Slightly prefer moves that reduce distance to the nearest unclaimed cell
        nearest_un = None
        if unclaimed:
            for ux, uy in unclaimed:
                d = abs(ux - nx) + abs(uy - ny)
                if nearest_un is None or d < nearest_un:
                    nearest_un = d
            if nearest_un is not None:
                score += max(0, 30 - nearest_un) * 1.5

        # Avoid "trapping" by stepping onto opponent territory unless it has nearby unclaimed
        if (nx, ny) in opp_t:
            score += local_unclaimed_count(nx, ny) * 6

        # Deterministic tie-break: fixed order of dirs and then lexicographic
        if score > best_score or (score == best_score and (ddx, ddy) < (best[0], best[1])):
            best_score = score
            best = [ddx, ddy]

    return [int(best[0]), int(best[1])]