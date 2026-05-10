def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                unclaimed.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    # If no unclaimed, try to take opponent territory or just head away from it slightly
    if not unclaimed and not opp_terr:
        return [0, 0]

    candidates = []
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in self_terr:
            base = 0.0
        elif (nx, ny) in opp_terr:
            base = 5.0
        elif (nx, ny) in unclaimed:
            base = 3.0
        else:
            base = -1.0  # likely opponent territory not listed, or unreachable

        # Prefer stepping onto/near our frontier to keep expanding steadily
        frontier_bonus = 0.0
        for ax, ay in dirs8:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in self_terr:
                frontier_bonus = 1.5
                break

        # Prefer moving toward nearby unclaimed; also avoid getting stuck next to obstacles isn't needed since obstacles are filtered
        dist_un = 0
        if unclaimed:
            best = 10**9
            # local deterministic look: consider up to 12 closest by simple scan
            for i, (ux, uy) in enumerate(unclaimed):
                d = abs(ux - nx) + abs(uy - ny)
                if d < best:
                    best = d
                if i >= 11 and best == 0:
                    break
            dist_un = best
        # dist_un smaller is better -> subtract
        goal_term = (-0.35 * dist_un) if unclaimed else 0.0

        # Secondary: do not allow opponent to immediately close; head toward them only when capturing is possible
        threat = 0.0
        if (nx, ny) in opp_terr:
            threat = -0.2 * (abs(nx - ox) + abs(ny - oy))

        val = base + frontier_bonus + goal_term + threat
        candidates.append((val, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], dirs8.index((t[1], t[2]))))
    return [int(candidates[0][1]), int(candidates[0][2])]