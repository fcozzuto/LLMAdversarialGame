def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in role) or ("purs" in opp_role and "evad" not in role)
    evader = not pursuer

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x, y): 
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy  # squared Euclidean

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        d = dist(nx, ny)
        mob = mobility(nx, ny)

        # Immediate capture / avoidance with higher priority
        if nx == ox and ny == oy:
            score = 10**9 if pursuer else -10**9
        else:
            # Pursuer: minimize distance, maximize mobility slightly
            # Evader: maximize distance, maximize mobility slightly
            # Add a small bias to favor progressing around obstacles deterministically:
            # prefer reducing (or increasing) manhattan to opponent along x, then y.
            manh = abs(nx - ox) + abs(ny - oy)
            sx_m = (1 if nx > ox else (-1 if nx < ox else 0))
            sy_m = (1 if ny > oy else (-1 if ny < oy else 0))
            bias = (sx_m + 2 * sy_m) * 0.01

            if pursuer:
                score = -d + 0.3 * mob + 0.05 * (-manh) + bias
            else:
                score = d + 0.3 * mob + 0.05 * manh + bias

        if best_score is None:
            best_score = score
            best_move = [dx, dy]
        else:
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
            elif score == best_score:
                # Deterministic tie-break: prefer moves with larger |dx|, then larger |dy|, then staying last
                def tkey(m):
                    mdx, mdy = m[0], m[1]
                    return (abs(mdx), abs(mdy), 1 if (mdx == 0 and mdy == 0) else 0)
                if tkey([dx, dy]) > tkey(best_move):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]