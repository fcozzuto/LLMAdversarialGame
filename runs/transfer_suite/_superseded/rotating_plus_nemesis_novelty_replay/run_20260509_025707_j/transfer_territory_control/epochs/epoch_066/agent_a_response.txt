def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    ox, oy = observation["opponent_position"]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    myc = observation.get("self_territory_count", len(my_set))
    opc = observation.get("opponent_territory_count", len(opp_set))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Defensive if we're behind: grow into unclaimed away from opponent.
    # Offensive if ahead/close: opportunistically step onto opponent territory.
    behind = myc < opc
    w_gain = 3 if behind else 2
    w_flip = 5 if not behind else 3
    w_away = 2 if behind else 1

    best = (float("-inf"), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        cell = (nx, ny)
        score = 0
        if cell in my_set:
            score += 0
        elif cell in unclaimed:
            score += w_gain
        elif cell in opp_set:
            score += w_flip
        # Prefer positions that are harder for the opponent to immediately sweep.
        d_before = dist((sx, sy), (ox, oy))
        d_after = dist((nx, ny), (ox, oy))
        score += w_away * (d_after - d_before)
        # Encourage moves toward the nearest unclaimed when behind; toward nearest opponent when ahead.
        if unclaimed:
            target = min(unclaimed, key=lambda p: dist((nx, ny), p))
            score += (-1 if not behind else 1) * (0.08 * dist((nx, ny), target))
        if opp_set:
            t2 = min(opp_set, key=lambda p: dist((nx, ny), p))
            score += (0.08 if not behind else -0.08) * dist((nx, ny), t2)
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [best[1], best[2]]