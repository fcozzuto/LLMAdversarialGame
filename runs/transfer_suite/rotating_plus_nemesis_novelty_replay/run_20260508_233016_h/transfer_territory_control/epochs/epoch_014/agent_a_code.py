def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    unclaimed_list = list(unclaimed)
    if unclaimed_list:
        nearest_unclaimed = min(unclaimed_list, key=lambda c: man((sx, sy), c))
        base_dn = man((sx, sy), nearest_unclaimed)
    else:
        nearest_unclaimed, base_dn = None, 99

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        score = 0.0
        if cell in self_terr:
            score += 0.1
        if cell in unclaimed:
            score += 1.0
        if cell in opp_terr:
            score += 1.6  # flipping on entry enabled

        if nearest_unclaimed is not None:
            dn = man((nx, ny), nearest_unclaimed)
            score += (base_dn - dn) * 0.03

        # Contest when close to opponent frontier; otherwise drift away a bit
        do = man((nx, ny), opp_pos)
        score += (6 - do) * 0.02

        # Deterministic tie-break: fixed order by score then (dx,dy)
        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move