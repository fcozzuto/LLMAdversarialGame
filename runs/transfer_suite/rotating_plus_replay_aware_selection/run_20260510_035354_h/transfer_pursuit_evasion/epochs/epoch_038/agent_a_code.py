def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in role) or ("purs" in opp_role and "evad" not in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def d2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for mx, my in moves:
            nx, ny = x + mx, y + my
            if inside(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    # Prefer deterministic tie-breaking toward staying still then lexicographic by move.
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        md = mobility(nx, ny)
        prev_md = mobility(sx, sy)
        center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) * 0.0001
        dist = d2(nx, ny)

        if nx == ox and ny == oy:
            score = 10**9 if pursuer else -10**9
        else:
            # Wall-run evasion often fails when mobility collapses; incorporate mobility delta.
            mob_delta = (md - prev_md)
            if pursuer:
                score = (-dist) + 0.25 * md + 0.1 * mob_delta + center_bias
            else:
                score = (dist) + 0.25 * md - 0.1 * mob_delta + center_bias

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer (0,0), then smaller dx, then smaller dy
            if best_move != [0, 0] and [dx, dy] == [0, 0]:
                best_move = [dx, dy]
            elif best_move != [0, 0] and [dx, dy] != [0, 0]:
                if (dx, dy) < (best_move[0], best_move[1]):
                    best_move = [dx, dy]

    return best_move