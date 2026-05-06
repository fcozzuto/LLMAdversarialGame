def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # If we are alone in edge/corner, still race resources; keep deterministic.
    opp_on_edge = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        invalid = (not inb(nx, ny)) or ((nx, ny) in obstacles)
        if invalid:
            nx, ny = sx, sy
        my_d_near = min(man(nx, ny, rx, ry) for rx, ry in resources)
        opp_d_near = min(man(ox, oy, rx, ry) for rx, ry in resources)

        # Race contest term: best resource where we are relatively closer than opponent.
        best_race = -10**9
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            diff = d_op - d_me
            if diff > best_race:
                best_race = diff

        # Extra shaping: avoid landing on/adjacent to obstacles (via hard penalty if move invalid).
        penalty = 6 if invalid else 0
        # Edge patrol counter: if opponent is on edge, value contests slightly more.
        edge_bonus = 2 if opp_on_edge else 0

        score = (opp_d_near - my_d_near) * (5 + edge_bonus) + best_race * 2 - my_d_near - penalty

        # Deterministic tie-break: prefer non-stay and moves that decrease distance to nearest resource.
        cur_my_near = min(man(sx, sy, rx, ry) for rx, ry in resources)
        key = (-(score), invalid, 0 if (dx != 0 or dy != 0) else 1, my_d_near - cur_my_near, dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]