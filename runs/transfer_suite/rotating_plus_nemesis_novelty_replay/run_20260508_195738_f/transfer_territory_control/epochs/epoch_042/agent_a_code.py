def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    opp_terr = observation.get("opponent_territory", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])

    opp_set = set((p[0], p[1]) for p in opp_terr)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda nx, ny: 0 <= nx < w and 0 <= ny < h

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    candidates = []
    target_list = opp_terr if opp_terr else unclaimed
    if target_list:
        best_t = None
        best_d = 10**9
        for tx, ty in target_list:
            d = manh((x, y), (tx, ty))
            if d < best_d:
                best_d, best_t = d, (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = opp_pos[0], opp_pos[1]

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer captures first, then expanding into unclaimed, while moving closer to target.
        if (nx, ny) in opp_set:
            base = 1000
        elif [nx, ny] in (unclaimed or []):
            base = 50
        else:
            base = 0
        d_to_target = manh((nx, ny), (tx, ty))
        d_curr = manh((x, y), (tx, ty))
        progress = d_curr - d_to_target  # positive is good
        # Slight bias toward pushing toward opponent even without capture.
        opp_bias = manh((nx, ny), (opp_pos[0], opp_pos[1]))
        candidates.append((base * 2 + progress * 10 - opp_bias, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]