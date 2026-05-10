def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    sx, sy = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])
    obstacles = observation.get("obstacles", [])
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)
    self_role = observation.get("self_role", "")
    opp_role = observation.get("opponent_role", "")
    pursuer = (self_role.lower().find("purs") != -1) or (opp_role.lower().find("evad") != -1 and self_role.lower().find("evad") == -1)
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if pursuer:
            score = -d2  # maximize negative distance (i.e., minimize distance)
        else:
            score = d2   # maximize distance
        if best is None:
            best, best_score = (dx, dy), score
        else:
            if score > best_score if not pursuer else score > best_score:
                best, best_score = (dx, dy), score
            elif score == best_score:
                # deterministic tie-break: prefer moves that align with objective direction
                # pursuer: prefer dx toward opponent then dy; evader: prefer opposite
                dirx = 0 if ox == sx else (1 if ox > sx else -1)
                diry = 0 if oy == sy else (1 if oy > sy else -1)
                tx = dirx if pursuer else -dirx
                ty = diry if pursuer else -diry
                cand = (dx, dy)
                pref_best = (best[0] - tx, best[1] - ty)
                pref_cand = (cand[0] - tx, cand[1] - ty)
                mag_best = abs(pref_best[0]) + abs(pref_best[1])
                mag_cand = abs(pref_cand[0]) + abs(pref_cand[1])
                if mag_cand < mag_best:
                    best = cand
                elif mag_cand == mag_best:
                    # final deterministic order
                    if cand < best:
                        best = cand
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]