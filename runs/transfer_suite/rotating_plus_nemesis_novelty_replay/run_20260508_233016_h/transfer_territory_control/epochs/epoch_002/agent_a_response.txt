def choose_move(observation):
    x, y = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obs = set(tuple(p) for p in observation.get("obstacles", []))
    self_terr = set(tuple(p) for p in observation.get("self_territory", []))
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory", []))
    uncl = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opponent_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opponent_pos[0], opponent_pos[1]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def md(a, b):
        d = a - b
        if d < 0:
            d = -d
        return d

    def dist_manh(px, py, qx, qy):
        return md(px, qx) + md(py, qy)

    # nearest unclaimed distance from current (for consistent tie-breaking)
    cur_best = 10**9
    for ux, uy in uncl:
        d = dist_manh(x, y, ux, uy)
        if d < cur_best:
            cur_best = d

    best_mv = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        score = 0.0
        if (nx, ny) in uncl:
            score += 500.0
        elif (nx, ny) in opp_terr:
            score += 220.0  # flipping is enabled on entry
        elif (nx, ny) in self_terr:
            score += 20.0
        else:
            score += 5.0  # staying in neutral/transition

        # distance shaping to push into territory growth fronts
        if uncl:
            best_d = 10**9
            for ux, uy in uncl:
                d = dist_manh(nx, ny, ux, uy)
                if d < best_d:
                    best_d = d
            score += max(0.0, (cur_best - best_d)) * 40.0
            score += -best_d * 3.0

        # keep pressure toward center
        score += - (dist_manh(nx, ny, cx, cy) if isinstance(cx, float) else dist_manh(nx, ny, int(cx), int(cy))) * 0.8

        # avoid marching straight into opponent control unless we take it
        if (nx, ny) not in opp_terr:
            score += -dist_manh(nx, ny, ox, oy) * 0.15

        # tie-break deterministically: prefer staying only if not worse, then lexicographic move
        mv = (dx, dy)
        if score > best_score or (score == best_score and mv < tuple(best_mv)):
            best_score = score
            best_mv = [dx, dy]

    return best_mv