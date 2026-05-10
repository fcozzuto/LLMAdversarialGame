def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [0, 0])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(x), int(y)) for x, y in unclaimed if x is not None and y is not None)

    their_terr = observation.get("opponent_territory") or []
    their_set = set((int(x), int(y)) for x, y in their_terr if x is not None and y is not None)

    our_terr = observation.get("self_territory") or []
    our_set = set((int(x), int(y)) for x, y in our_terr if x is not None and y is not None)

    adj_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    neigh8 = adj_dirs

    # Candidate targets: unclaimed adjacent to opponent, else adjacent to our territory, else any unclaimed.
    cand = []
    for x, y in their_set:
        for dx, dy in adj_dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in un_set:
                cand.append((nx, ny))

    if not cand and our_set:
        for x, y in our_set:
            for dx, dy in adj_dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in un_set:
                    cand.append((nx, ny))

    if not cand:
        cand = list(un_set) if un_set else [(sx, sy)]
    else:
        # Deduplicate while keeping deterministic order
        cand = list(dict.fromkeys(cand))

    # Score candidates deterministically: pressure opponent + potential expansion (nearby unclaimed density).
    def density(x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in un_set:
                c += 1
        return c

    best = None
    best_score = None
    for x, y in cand:
        # Prefer closer to opponent and with higher local unclaimed density; small preference to closer to us.
        dist_to_opp = abs(x - ox) + abs(y - oy)
        dist_to_us = abs(x - sx) + abs(y - sy)
        dens = density(x, y)
        score = (-2.0 * dist_to_opp) + (1.5 * dens) + (-0.3 * dist_to_us)
        if best is None or score > best_score or (score == best_score and (x, y) < best):
            best_score = score
            best = (x, y)

    tx, ty = best if best is not None else (sx, sy)

    # Choose move that minimizes distance to target while staying valid.
    best_move = (0, 0)
    best_d = None
    for dx, dy in adj_dirs + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]