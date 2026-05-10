def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    self_terr = set((a, b) for a, b in observation.get("self_territory", []))
    opp_terr = set((a, b) for a, b in observation.get("opponent_territory", []))
    unclaimed = observation.get("unclaimed_cells", [])
    uncl = set((a, b) for a, b in unclaimed)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_score = -10**18

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Precompute nearest unclaimed distance from current position
    cur_uncl_dist = 10**9
    for ux, uy in unclaimed:
        d = dist(x, y, ux, uy)
        if d < cur_uncl_dist:
            cur_uncl_dist = d

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        target_is_uncl = (nx, ny) in uncl
        target_is_opp = (nx, ny) in opp_terr
        target_is_self = (nx, ny) in self_terr

        score = 0
        if target_is_uncl:
            score += 300
        elif target_is_opp:
            score += 200
        elif target_is_self:
            score += 50
        else:
            score += 10

        # Progress toward nearest unclaimed (deterministic, cheap scan)
        nd = 10**9
        for ux, uy in unclaimed:
            d = dist(nx, ny, ux, uy)
            if d < nd:
                nd = d
        if nd == 10**9:
            nd = cur_uncl_dist

        score += (cur_uncl_dist - nd) * 30

        # Prefer slightly increasing distance from opponent to reduce contest pressure
        od_cur = dist(x, y, ox, oy)
        od_new = dist(nx, ny, ox, oy)
        score += (od_new - od_cur) * 5

        # Avoid stepping into immediate opponent proximity unless capturing something
        if not target_is_uncl and od_new <= 1:
            score -= 120

        if score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score and best is not None:
            # Deterministic tie-break: lexicographic on (dx, dy)
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]