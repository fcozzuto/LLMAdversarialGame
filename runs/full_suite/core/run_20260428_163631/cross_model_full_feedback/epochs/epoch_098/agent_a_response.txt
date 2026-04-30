def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = [(dx, dy) for dx, dy in deltas if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    # If standing on a resource-adjacent path is best, prioritize it.
    if resources:
        # Pick a primary target: nearest resource, tie-broken by being further from opponent.
        def target_key(r):
            return (dist(me, r), -dist(opp, r))
        target = min(resources, key=target_key)

        best_move = (0, 0)
        best_score = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            np = (nx, ny)

            # Big reward for stepping onto any resource.
            res_reward = 0
            if np in obstacles:
                continue
            if np in resources:
                res_reward = 1000 - dist(opp, np)

            # Encourage moving closer to target and, secondarily, other nearby resources.
            d_to_target = dist(np, target)
            nearest_other = min(resources, key=lambda r: dist(np, r))
            d_nearest_other = dist(np, nearest_other)

            # Avoid allowing opponent to take the same target area first.
            # Prefer states where we are not much farther than opponent from the target.
            opp_next = dist(opp, target)
            my_adv = dist(np, target) - opp_next  # lower is better

            # Keep some spacing from opponent (prevents close chases when contested).
            spacing = dist(np, opp)

            score = (res_reward
                     + (-10 * d_to_target)
                     + (-3 * d_nearest_other)
                     + (-2.5 * my_adv)
                     + (0.8 * min(spacing, 6)))
            # Deterministic tie-break: prefer smaller dx then dy
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: drift to center while staying away from opponent.
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in legal:
        np = (sx + dx, sy + dy)
        score = (-dist(np, (cx, cy)) + 1.5 * min(dist(np, opp), 6))
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]