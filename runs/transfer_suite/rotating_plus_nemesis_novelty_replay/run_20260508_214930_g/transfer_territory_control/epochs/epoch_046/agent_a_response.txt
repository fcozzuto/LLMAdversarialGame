def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if unclaimed:
        # Prefer far-from-opponent unclaimed (deny center), but closest to us among them.
        candidates = []
        for x, y in unclaimed:
            if (x, y) in obstacles:
                continue
            candidates.append((man(x, y, ox, oy), man(sx, sy, x, y), x, y))
        far_dist, us_dist, tx, ty = max(candidates, key=lambda t: (t[0], -t[1], -t[2], -t[3]))
    else:
        # Fallback target: bias to our corner away from opponent.
        tx = 0 if ox > w // 2 else w - 1
        ty = 0 if oy > h // 2 else h - 1

    best = (0, 0)
    best_score = -10**18
    base_to_target = man(sx, sy, tx, ty)
    base_to_opp = man(sx, sy, ox, oy)

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        score = 0

        if (nx, ny) in opp_t:
            score += 900  # flipping on entry
        elif (nx, ny) in unclaimed:
            score += 70
        elif (nx, ny) in self_t:
            score += 10

        to_target = man(nx, ny, tx, ty)
        to_opp = man(nx, ny, ox, oy)

        score += (base_to_target - to_target) * 6          # move toward target
        score += (to_opp - base_to_opp) * 3               # keep distance from center-leaning opponent
        score += (1 if (nx, ny) in self_t else 0) * 2
        score -= (1 if (nx, ny) in opp_t else 0) * 2

        # Small preference for edges to counter center claim
        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        score += 8 if edge else 0

        if score > best_score or (score == best_score and (ddx, ddy) < best):
            best_score = score
            best = (ddx, ddy)

    return [int(best[0]), int(best[1])]