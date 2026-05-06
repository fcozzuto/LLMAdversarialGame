def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy), abs(dx) + abs(dy))
            if bestv is None or v < bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    res_set = set(tuple(p) for p in resources)
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        on_res = 1 if (nx, ny) in res_set else 0

        best_target_lead = -10**9
        best_target_dist = 10**9
        for rx, ry in resources:
            se = abs(nx - rx) + abs(ny - ry)
            oe = abs(ox - rx) + abs(oy - ry)
            lead = oe - se
            # Prefer moving onto resources and, if not, contest resources where opponent is closer.
            if (rx, ry) == (nx, ny):
                lead += 1000
            if lead > best_target_lead or (lead == best_target_lead and se < best_target_dist):
                best_target_lead, best_target_dist = lead, se

        # Additional pressure: avoid giving opponent immediate advantage by not increasing their closeness
        # to our chosen best target (approximated by global best target lead).
        v = (
            -(best_target_lead),          # maximize lead -> minimize negative
            abs(nx - ox) + abs(ny - oy), # keep some spacing
            abs(dx) + abs(dy),            # slight preference for smaller moves
            -on_res                        # landing on resource should win ties
        )
        candidates.append((v, dx, dy))

    candidates.sort(key=lambda t: t[0])
    return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]