def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def move_ok(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if move_ok(dx, dy)]
    if not cand:
        return [0, 0]

    # Evaluate each move by best resource "win potential" from resulting position.
    best_move = cand[0]
    best_val = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        my_pos = (nx, ny)
        opp_pos = (ox, oy)
        # Smaller is better for us; prefer resources where we can arrive no later than opponent.
        # Tie-break deterministically by closeness and then by resource coordinates.
        val = -10**18
        for tx, ty in resources:
            r = (tx, ty)
            my_d = man(my_pos, r)
            opp_d = man(opp_pos, r)
            # Score: prioritize arriving first; if opponent arrives earlier, heavily penalize.
            reach_diff = opp_d - my_d  # positive => we can reach sooner
            s = reach_diff * 100 - my_d
            # Strongly discourage contested grabs where opponent is closer by 1+.
            if reach_diff < 0:
                s -= 1000 + (-reach_diff) * 50
            # Mild preference for higher "safety": avoid too-far targets.
            s -= (my_d > 6) * 30
            # Deterministic tie-break
            s -= (tx * 0.01 + ty * 0.001)
            if s > val:
                val = s
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]