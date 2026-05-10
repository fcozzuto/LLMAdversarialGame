def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        obs.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in role) or ("purs" in opp_role and "evad" not in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def manh(x, y): return abs(x - ox) + abs(y - oy)

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            v = -10**9 if pursuer else -10**9
        else:
            d = manh(nx, ny)
            if nx == ox and ny == oy:
                v = 10**9 if pursuer else -10**9
            else:
                mob = mobility(nx, ny)
                adj = 0
                for ax, ay in obs:
                    if abs(nx - ax) <= 1 and abs(ny - ay) <= 1:
                        adj += 1
                # pursuer: minimize distance; evader: maximize distance
                v = (-(d * 10) + mob * 2 - adj * 3) if pursuer else ((d * 10) + mob * 2 - adj * 3)
                # slight bias to keep moving (helps against zigzag evasion)
                v += (1 if (dx != 0 or dy != 0) else -1) * (1 if pursuer else 1)
                # prefer not to step into immediate "corridors" for evader; opposite for pursuer
                v += ((mob - 3) * 1.5)
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]