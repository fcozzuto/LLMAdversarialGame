def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def min_dist_to_set(x, y, s):
        md = 10**9
        for (px, py) in s:
            d = abs(px - x) + abs(py - y)
            if d < md:
                md = d
        return md if md != 10**9 else 0

    frontier = [(x, y) for (x, y) in self_t if (x, y) in self_t]
    base_dist = abs(sx - ox) + abs(sy - oy)

    best = (0, 0)
    best_score = -10**18

    # Prefer expanding from our territory while taking nearby opp territory; also pressure towards opponent side.
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 1200  # decisive if we can flip/steal
        if (nx, ny) in unclaimed:
            score += 80
        if (nx, ny) in self_t:
            score += 10

        # Frontier bonus: move that tends to grow boundary (adjacent to our territory).
        adj_own = 0
        for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx+1, ny+1), (nx-1, ny+1), (nx+1, ny-1)):
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in self_t:
                adj_own += 1
        score += adj_own * 12

        # Distance shaping: get closer to our "front" towards opponent, but not suicide into opponent core.
        if self_t:
            score += (min_dist_to_set(nx, ny, self_t) * -1)  # smaller is better
        score += (base_dist - (abs(nx - ox) + abs(ny - oy))) * 3  # prefer moves that reduce opponent separation

        # Avoid stepping into areas heavily surrounded by opponent territory (can be counter-flipped).
        if opp_t:
            score += (min_dist_to_set(nx, ny, opp_t) * -2)  # smaller dist to opponent reduces score slightly
        # Prefer staying near our own side if we are currently leading heavily (reduce risk of being intercepted).
        if observation.get("self_territory_count", 0) > observation.get("opponent_territory_count", 0) + 8:
            score += (abs(nx - sx) + abs(ny - sy)) * -1

        if score > best_score:
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]