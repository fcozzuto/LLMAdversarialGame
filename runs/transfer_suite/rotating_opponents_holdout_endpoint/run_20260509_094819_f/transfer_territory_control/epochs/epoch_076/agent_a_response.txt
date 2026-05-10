def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []) if x is not None)
    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def nearest_dist_to_set(x, y, s):
        if not s:
            return 999
        return min(man(x, y, tx, ty) for tx, ty in s)

    prefer_unclaimed = True if unclaimed else False
    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        cell = (nx, ny)
        is_unclaimed = cell in unclaimed
        is_opp = cell in opp_t
        is_self = cell in self_t

        # Territory-edge-claim counter: move toward uncontested interior (maximize distance from opponent),
        # while preferring unclaimed captures over direct fighting.
        dist_opp = nearest_dist_to_set(nx, ny, opp_t) if opp_t else 999
        dist_self = nearest_dist_to_set(nx, ny, self_t) if self_t else 0
        dist_unclaimed = nearest_dist_to_set(nx, ny, unclaimed) if unclaimed else 0

        base = 0
        if prefer_unclaimed and is_unclaimed:
            base += 120
        elif is_unclaimed:
            base += 60
        if is_opp:
            base += 25  # allow flips, but don't chase blindly
        if is_self:
            base += 8

        # Encourage spreading away from opponent and toward nearest frontier.
        score = base + (dist_opp * 6) + (max(0, 6 - dist_self) * 2) + (max(0, 6 - dist_unclaimed) * 3)

        # Deterministic tie-breaker: prefer smaller dx, then smaller dy, then staying still last.
        tie = (-abs(dx), -abs(dy), dx == 0 and dy == 0)
        key = (score, tie)
        if best is None or key > best:
            best = key
            best_score = score
            best_move = [dx, dy]

    return best_move