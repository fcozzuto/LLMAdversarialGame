def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def val(tx, ty, cx, cy):
        d_me = abs(tx - cx) + abs(ty - cy)
        d_opp = abs(tx - ox) + abs(ty - oy)
        return (d_opp - d_me) * 1000 - d_me + (d_opp * 0.01)

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = x, y  # engine likely keeps us; keep deterministic score consistent

        chosen = resources[0]
        best_v = val(chosen[0], chosen[1], nx, ny)
        for r in resources[1:]:
            tv = val(r[0], r[1], nx, ny)
            if tv > best_v:
                best_v = tv
                chosen = r

        tx, ty = chosen[0], chosen[1]
        d_me = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Tie-break: prefer larger advantage, then smaller self distance, then lexicographic target
        score = (best_v, d_opp - d_me, -d_me, -tx, -ty)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move