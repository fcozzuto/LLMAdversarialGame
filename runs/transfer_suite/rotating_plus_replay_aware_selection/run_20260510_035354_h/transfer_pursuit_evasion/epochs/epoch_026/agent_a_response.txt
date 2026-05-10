def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)
    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_pursuer = ("purs" in role) or ("evad" not in role and ("evad" in opp_role or "evader" in opp_role))
    dxs = (-1, 0, 1); dys = (-1, 0, 1)

    def clamp_score(val):
        return 10**9 if val is None else val

    best_move = [0, 0]
    best_val = None

    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            md = abs(nx - ox) + abs(ny - oy)
            # Prefer moving to reduce (pursuit) / increase (evasion) Manhattan distance,
            # and break ties by favoring alignment with opponent direction.
            sxdir = 1 if ox > sx else (-1 if ox < sx else 0)
            sydir = 1 if oy > sy else (-1 if oy < sy else 0)
            align = (dx == sxdir) + (dy == sydir)
            next_alts = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0:
                        continue
                    tx, ty = nx + adx, ny + ady
                    if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs:
                        next_alts += 1
            # Wall-runner handling: avoid moves that trap us (low mobility) when pursuing,
            # and avoid giving opponent a big escape channel when evading.
            mobility = next_alts
            if i_pursuer:
                val = md * 1000 - align * 10 - mobility
                better = best_val is None or val < best_val
            else:
                val = -md * 1000 + align * 10 + mobility
                better = best_val is None or val > best_val
            if better:
                best_val = val
                best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_move