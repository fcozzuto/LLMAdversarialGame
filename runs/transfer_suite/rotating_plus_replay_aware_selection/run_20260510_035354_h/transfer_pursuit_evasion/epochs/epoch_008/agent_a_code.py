def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set(tuple(p) for p in observation.get("obstacles", []))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    is_pursuer = ("purs" in self_role) or (self_role == "pursuer") or (("evad" in opp_role) and ("purs" in self_role))
    if not self_role:
        is_pursuer = False
    if ("evad" in self_role) or (self_role == "evader") or ("evad" in self_role):
        is_pursuer = False
    if ("purs" in opp_role) and ("evad" not in self_role) and ("purs" not in self_role):
        # if we don't know but opponent is pursuer, we are likely evader
        is_pursuer = False

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Deterministic scoring targets
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if is_pursuer:
        target = (ox, oy)
    else:
        # Evader: prefer farthest corner from opponent, but keep greedy distancing too
        bestc = corners[0]
        bestd = man(bestc[0], bestc[1], ox, oy)
        for c in corners[1:]:
            d = man(c[0], c[1], ox, oy)
            if d > bestd:
                bestd = d
                bestc = c
        target = bestc

    best_move = moves[0]
    if is_pursuer:
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            # Greedy chase with slight preference for moving toward opponent's vicinity
            sc = -d * 100 + (-man(nx, ny, target[0], target[1]))
            if sc > best_score:
                best_score = sc
                best_move = (dx, dy)
    else:
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            # Greedy evade with slight preference for corners and away from opponent
            sc = d * 100 - man(nx, ny, target[0], target[1])
            if sc > best_score:
                best_score = sc
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]