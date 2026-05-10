def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    self_set = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) == 2)
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) == 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            cand.append((dx, dy))
    if not cand:
        return [0, 0]

    def dist(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax + ay

    # Precompute nearest unclaimed distance for shaping (small cap for determinism)
    un_list = list(un_set)
    cap = 24 if len(un_list) > 24 else len(un_list)
    un_list = un_list[:cap]

    def nearest_un_dist(x, y):
        if not un_list:
            return 0
        best = None
        for ux, uy in un_list:
            d = dist(x, y, ux, uy)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    # Immediate gain heuristic + expansion and safety
    best_move = None
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        edge = 0.25 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0.0
        if (nx, ny) in self_set:
            gain = 0.0
        elif (nx, ny) in un_set:
            gain = 1.0
        elif (nx, ny) in opp_set:
            # flipping: opponent loses a cell, we gain it
            gain = 2.0
        else:
            gain = 0.2

        d_to_enemy = dist(nx, ny, ox, oy)
        enemy_pressure = -0.08 * d_to_enemy

        d_un = nearest_un_dist(nx, ny)
        expand = -0.15 * d_un

        # Prefer moves that reduce distance to opponent while being on likely flip/unclaimed
        flip_bias = 0.0
        if (nx, ny) in opp_set or (nx, ny) in un_set:
            flip_bias = 0.12 * (dist(sx, sy, ox, oy) - dist(nx, ny, ox, oy))

        score = gain + edge + enemy_pressure + expand + flip_bias
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]