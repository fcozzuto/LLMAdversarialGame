def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    self_terr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_terr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    nbrs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    # Decide focus: when we are small/behind, push unclaimed; otherwise contest near opponent.
    myc = int(observation.get("self_territory_count") or 0)
    oppc = int(observation.get("opponent_territory_count") or 0)
    behind = (myc <= oppc)

    best = [0, 0]
    best_val = -10**18

    # Precompute a small deterministic target preference
    targets = []
    if behind and unclaimed:
        targets = sorted(unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[1], t[0]))[:8]
    elif opp_terr:
        targets = sorted(opp_terr, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[1], t[0]))[:8]

    for dx, dy in nbrs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        ncell = (nx, ny)
        val = 0.0

        if ncell in opp_terr:
            val += 3.0  # flipping into opponent territory
            if behind:
                val += 1.0
        elif ncell in unclaimed or ncell not in self_terr:
            # unclaimed generally increases controlled area
            val += 2.0
            if behind:
                val += 0.5

        # Prefer expanding outward and pushing towards center when not behind
        dcen = abs(nx - cx) + abs(ny - cy)
        val += (0.25 if not behind else 0.05) * (-dcen)

        # If we have candidate targets, greedily reduce distance to the best one.
        if targets:
            mind = 10**9
            for tx, ty in targets:
                dd = abs(tx - nx) + abs(ty - ny)
                if dd < mind:
                    mind = dd
            val += -0.9 * mind

        # Tiny preference for staying still only when no positive option exists
        if (dx, dy) == (0, 0):
            val -= 0.05

        if val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best = [dx, dy]

    return best