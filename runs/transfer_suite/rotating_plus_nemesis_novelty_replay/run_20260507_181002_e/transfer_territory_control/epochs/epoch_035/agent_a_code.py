def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not unclaimed:
        unclaimed = set()

    # Heuristic weights: unclaimed first, then opponent territory (flip), otherwise expand toward frontier.
    # Also avoid moving into positions from which opponent is likely to claim back (adjacent to opponent).
    opp_adj = {(ox + dx, oy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)}
    self_count = int(observation.get("self_territory_count", len(selfT)))
    opp_count = int(observation.get("opponent_territory_count", len(oppT)))
    aggressiveness = 1.0 if opp_count >= self_count else 0.7

    best = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        in_self = (nx, ny) in selfT
        in_opp = (nx, ny) in oppT
        in_un = (nx, ny) in unclaimed

        # Distances (cheaper than global search)
        d_to_center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        d_to_opp = abs(nx - ox) + abs(ny - oy)

        # Immediate gain proxy
        gain = 0.0
        if in_un:
            gain += 8.0
        if in_opp:
            gain += 10.0 * aggressiveness + (5.0 / (1 + d_to_opp))
        if in_self:
            gain -= 0.2

        # Counterclaim risk: don't step adjacent to opponent unless it flips their territory
        risk = 0.0
        if (nx, ny) in opp_adj and not in_opp:
            risk += 4.5

        # Frontier pressure: prefer moving away from our stable zones and toward opponent direction early,
        # but keep it symmetric by also favoring center later.
        center_pull = -0.15 * d_to_center
        toward_opp = 0.25 * (-(d_to_opp))
        move_pref = 0.05 * (dx == 0 and dy == 0)  # slight bias to stay only if tied

        score = gain + center_pull + toward_opp - risk + move_pref
        if score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]