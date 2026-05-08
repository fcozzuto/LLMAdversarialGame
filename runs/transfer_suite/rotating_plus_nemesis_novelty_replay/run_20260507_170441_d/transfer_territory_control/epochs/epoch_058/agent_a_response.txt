def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    unclaimed_adj_opp = set()
    if opp_t and unclaimed:
        for ux, uy in unclaimed:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                if (ux + dx, uy + dy) in opp_t:
                    unclaimed_adj_opp.add((ux, uy))
                    break

    if unclaimed_adj_opp:
        targets = sorted(unclaimed_adj_opp, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        target = targets[0]
    elif unclaimed:
        # Otherwise grab nearest unclaimed cell near the opponent side (min distance to opponent + self)
        tlist = list(unclaimed)
        target = min(tlist, key=lambda p: (abs(p[0] - ox) + abs(p[1] - oy) + 0.3 * (abs(p[0] - sx) + abs(p[1] - sy)), p[0], p[1])) if tlist else (sx, sy)
    else:
        target = (ox, oy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-(10**18), 0, 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Heuristic scoring: move toward target; prefer opponent- adjacent or opponent-owned entry; avoid obstacles already handled.
        dist_to_target = abs(nx - target[0]) + abs(ny - target[1])
        score = -dist_to_target

        if (nx, ny) in opp_t:
            score += 120  # immediate flip/claim pressure
        else:
            # If we can step onto an unclaimed cell adjacent to opponent, that's strong.
            if (nx, ny) in unclaimed_adj_opp:
                score += 70
            elif unclaimed_adj_opp and any((nx + adx, ny + ady) in opp_t for adx, ady in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))):
                score += 20

        # Also bias toward frontier growth: prefer cells not already ours.
        if (nx, ny) in self_t:
            score -= 5

        # Deterministic tie-break: prefer moves with smaller (dx,dy) ordering toward right/down? use lex stable.
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]