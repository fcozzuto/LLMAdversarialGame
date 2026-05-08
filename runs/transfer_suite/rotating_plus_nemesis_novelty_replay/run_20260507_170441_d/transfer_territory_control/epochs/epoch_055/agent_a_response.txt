def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        x, y = p
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []

    # Prefer unclaimed cells adjacent to opponent territory.
    adj_targets = []
    if unclaimed and opp_t:
        for ux, uy in unclaimed:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                nx, ny = ux + dx, uy + dy
                if (nx, ny) in opp_t:
                    adj_targets.append((ux, uy))
                    break

    # Deterministically choose a "frontier" target.
    if adj_targets:
        tx, ty = min(adj_targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - ox) + abs(p[1] - oy), p[0], p[1]))
    else:
        # Fallback: closest unclaimed cell, else move toward opponent to create flipping pressure.
        if unclaimed:
            tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        else:
            tx, ty = ox, oy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    best = (-(10**9), 0, 0)
    for dx, dy in dirs:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in blocked:
            nx, ny = sx, sy
            dx, dy = 0, 0

        score = 0
        if (nx, ny) in opp_t:
            score += 120
            score += 20 - (abs(nx - ox) + abs(ny - oy)) * 0.1
        elif (nx, ny) in unclaimed:
            score += 35
            if adj_targets and any(abs(nx - ax) <= 1 and abs(ny - ay) <= 1 for ax, ay in opp_t):
                score += 20
        elif (nx, ny) in self_t:
            score += 4

        # Get closer to target.
        score += 18 - (abs(nx - tx) + abs(ny - ty)) * 0.9
        # Slightly prefer expanding away from obstacles via local clearance.
        neigh_free = 0
        for ddx, ddy in dirs:
            px, py = nx + ddx, ny + ddy
            if 0 <= px < w and 0 <= py < h and (px, py) not in blocked:
                neigh_free += 1
        score += neigh_free * 0.2

        # Tie-break deterministically toward reducing distance to opponent slightly.
        score += -0.05 * (abs(nx - ox) + abs(ny - oy))
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]