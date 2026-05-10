def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(a,b): return 0 <= a < w and 0 <= b < h

    def adj_to_opp(p):
        px, py = p
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if (nx, ny) in opp_ter:
                return True
        return False

    # Prefer denying opponent expansion: claim unclaimed cells adjacent to their territory.
    border_candidates = [c for c in unclaimed if adj_to_opp(c)]
    if border_candidates:
        def cand_key(c):
            cx, cy = c
            return (abs(cx - x) + abs(cy - y), abs(cx - ox) + abs(cy - oy))
        target = min(border_candidates, key=cand_key)
    elif unclaimed:
        target = min(unclaimed, key=lambda c: abs(c[0]-x) + abs(c[1]-y))
    else:
        # No unclaimed: try to keep/hold near our territory and drift away from opponent.
        target = (ox, oy)

    def move_score(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obs:
            return -10**9
        dcur = abs(ox - x) + abs(oy - y)
        dfut = abs(ox - nx) + abs(oy - ny)
        step_toward = -(abs(target[0]-nx) + abs(target[1]-ny))
        hold = 0
        if (nx, ny) in self_ter:
            hold += 120
        if (nx, ny) in opp_ter:
            hold -= 80  # entering opponent territory helps them advance too.
        deny = 0
        if (nx, ny) in unclaimed and adj_to_opp((nx, ny)):
            deny += 220
        # Encourage distance from opponent unless we are actively denying.
        away = 35 if dfut > dcur else -10
        return step_toward + hold + deny + away

    best = (0, 0)
    best_val = -10**18
    # Tie-break deterministically: prefer staying, then x- then y- direction order.
    order = [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
    for dx, dy in order:
        nx, ny = x + dx, y + dy
        val = move_score(nx, ny)
        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]