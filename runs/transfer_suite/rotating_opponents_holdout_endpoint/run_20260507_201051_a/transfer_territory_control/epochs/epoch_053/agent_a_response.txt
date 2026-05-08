def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    resources = observation.get("resources") or []
    unclaimed = observation.get("unclaimed_cells") or []
    targets = [tuple(p) for p in resources] if resources else [tuple(p) for p in unclaimed]

    if not targets:
        # Fallback: drift toward opponent to contest space; still deterministic.
        targets = [(ox, oy)]

    # Build simple "frontier" preference from unclaimed: cells near our territory.
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    near_frontier = []
    if unclaimed:
        for x, y in targets:
            if (x, y) in self_terr:
                continue
            # Encourage moves that reduce distance from us by 1-step neighborhood to our territory.
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    if (x + dx, y + dy) in self_terr:
                        near_frontier.append((x, y))
                        break
                else:
                    continue
                break
    if near_frontier:
        targets = near_frontier

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        p = (nx, ny)

        # Primary: go toward nearest target.
        d_t = min(manh(p, q) for q in targets)

        # Secondary: avoid getting too close to opponent unless it lets us hit unclaimed near them.
        d_o = manh(p, (ox, oy))

        # Tertiary: reward occupying unclaimed; penalize stepping into opponent territory (can flip but usually risky).
        on_unclaimed = 1 if (p in unclaimed) else 0
        on_opp = 1 if (p in opp_terr) else 0

        # Penalize staying only if we have meaningful targets.
        stay_pen = 1 if (dx == 0 and dy == 0) and d_t > 0 else 0

        # Combine into lexicographic-ish scalar; lower is better.
        score = (
            d_t,
            -d_o,            # farther from opponent is better
            -on_unclaimed,  # prefer unclaimed
            on_opp,         # avoid opponent territory unless it also is a target nearby
            stay_pen
        )

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]