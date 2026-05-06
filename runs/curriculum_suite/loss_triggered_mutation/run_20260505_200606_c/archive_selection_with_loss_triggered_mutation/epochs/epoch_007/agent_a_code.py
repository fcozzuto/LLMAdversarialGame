def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx * dx + dy * dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = -10**18

    if not resources:
        # Deterministic drift toward center while mildly anti-following opponent.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx = cx + (cx - ox) // 2
        ty = cy + (cy - oy) // 2
        tx = 0 if tx < 0 else (w - 1 if tx >= w else tx)
        ty = 0 if ty < 0 else (h - 1 if ty >= h else ty)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -d2(nx, ny, tx, ty)  # minimize distance to drift target
            if sc > best_score or (sc == best_score and (dx, dy) < best_move):
                best_score = sc
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose best resource by relative advantage, then break ties by proximity and lexicographic order.
    scored = []
    for rx, ry in resources:
        self_d = d2(sx, sy, rx, ry)
        opp_d = d2(ox, oy, rx, ry)
        adv = opp_d - self_d  # higher means we are closer than opponent
        # Add tiny bias for resources closer to our current position and not too far overall
        sc = adv * 100 - self_d
        scored.append((sc, -self_d, rx, ry))
    scored.sort(reverse=True)
    _, _, rx, ry = scored[0]

    # Take a greedy step toward chosen target, but evaluate locally to avoid obstacles.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = d2(nx, ny, rx, ry)
        # Also prefer moves that reduce opponent's access advantage.
        no = d2(ox, oy, rx, ry)
        sc = (no - ns) * 100 - ns
        if (nx, ny) == (rx, ry):
            sc += 10**7  # strongly favor stepping onto a resource if present
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    # If all candidate moves blocked, stay.
    return [best_move[0], best_move[1]]