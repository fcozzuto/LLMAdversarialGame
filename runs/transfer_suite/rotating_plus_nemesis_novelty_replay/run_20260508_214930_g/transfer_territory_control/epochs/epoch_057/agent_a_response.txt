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
    base_dist = abs(sx - ox) + abs(sy - oy)

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Small deterministic preference for "forward" (toward opponent) unless it risks getting stuck.
    forward = 1 if ox > sx else (-1 if ox < sx else 0)
    forward_y = 1 if oy > sy else (-1 if oy < sy else 0)

    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 2500  # flip/deny strongly
        elif (nx, ny) in unclaimed:
            score += 60

        if (nx, ny) in self_t:
            score += 8  # maintain/expand
        else:
            score += 0

        # Encourage pressure toward opponent and lateral progress into empty space.
        nd_opp = abs(nx - ox) + abs(ny - oy)
        score += (base_dist - nd_opp) * 3

        # Prefer moves that reduce distance to any unclaimed cell near opponent (frontier pressure).
        # Keep it cheap: sample at most 8 unclaimed cells deterministically.
        if unclaimed:
            best_front = 10**9
            cnt = 0
            for (ux, uy) in unclaimed:
                d = abs(ux - ox) + abs(uy - oy)
                if d < 9:  # near opponent region
                    best_front = min(best_front, abs(nx - ux) + abs(ny - uy))
                    cnt += 1
                    if cnt >= 8:
                        break
            if best_front < 10**9:
                score += max(0, 20 - best_front)

        # Avoid running away from opponent unless capturing/claiming.
        score += 2 * (dx == forward) + 2 * (dy == forward_y)

        # Slightly penalize moving into opponent territory only if it doesn't improve distance (more stable counterclaim).
        if (nx, ny) in opp_t and nd_opp > base_dist:
            score -= 600

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]