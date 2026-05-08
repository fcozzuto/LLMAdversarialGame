def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (sx, sy))
    ox, oy = int(ox), int(oy)

    def to_set(lst):
        s = set()
        for p in (lst or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                try:
                    x, y = int(x), int(y)
                except:
                    continue
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    self_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))

    targets_unclaimed = list(unclaimed)
    targets_opp = list(opp_t)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def min_dist_to_targets(x, y, targets):
        if not targets:
            return 10**9
        md = 10**9
        for tx, ty in targets:
            d = abs(x - tx) + abs(y - ty)
            if d < md:
                md = d
                if md == 0:
                    break
        return md

    best_score = -10**18
    best = (0, 0)
    have_uc = bool(targets_unclaimed)
    have_opp = bool(targets_opp)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 8
        if (nx, ny) in opp_t:
            score += 10
        if (nx, ny) in self_t:
            score += 2

        if have_uc:
            score += -2.5 * min_dist_to_targets(nx, ny, targets_unclaimed)
        elif have_opp:
            score += -2.0 * min_dist_to_targets(nx, ny, targets_opp)

        # Prefer moving away from opponent unless we can capture opponent territory.
        d_to_opp = man(nx, ny, ox, oy)
        score += 0.35 * d_to_opp
        score += -0.12 * (abs(nx - cx) + abs(ny - cy))

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]