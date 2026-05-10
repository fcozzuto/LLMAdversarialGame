def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if not unclaimed and not opp_t:
        return [0, 0]

    # Identify best "nearby" target deterministically: prefer unclaimed where we are closer than opponent
    opp_pos = observation["opponent_position"]
    targets = list(unclaimed) if unclaimed else []
    if not targets:
        targets = list(opp_t)

    best_t = None
    best_key = None
    for t in targets:
        d_s = abs(t[0]-sx) + abs(t[1]-sy)
        d_o = abs(t[0]-opp_pos[0]) + abs(t[1]-opp_pos[1])
        # higher is better; create lexicographic key for determinism
        advantage = d_o - d_s  # positive if we are closer
        key = (advantage, -d_s, t[0], t[1])
        if best_key is None or key > best_key:
            best_key = key
            best_t = t

    tx, ty = best_t

    # Evaluate one-step moves with a direct territory-focused heuristic
    best_m = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        new_cell = (nx, ny)
        score = 0
        if new_cell in unclaimed:
            score += 6
        if new_cell in opp_t:
            score += 10  # flipping on entry
        if new_cell in self_t:
            score += 2  # maintain control
        # push toward target; also avoid giving opponent immediate advantage by stepping into their cells unnecessarily
        d_to_t = abs(nx-tx) + abs(ny-ty)
        d_opp = abs(nx-opp_pos[0]) + abs(ny-opp_pos[1])
        score += (18 - 2*d_to_t) + (d_to_t * 0)  # keep integer
        score += (d_to_t - d_opp) * 0  # no float; placeholder neutral
        # tie-break deterministically: prefer moves that reduce distance to target then lexicographic
        key = (score, -d_to_t, nx, ny)
        if best_score is None or key > best_score:
            best_score = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]