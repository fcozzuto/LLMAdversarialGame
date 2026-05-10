def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Prefer expanding near opponent boundary; otherwise take best unclaimed edge/middle.
    target_cells = unclaimed[:]
    if not target_cells:
        # If no unclaimed, fight: move toward closest opponent cell adjacent to ours.
        boundary = []
        for ax, ay in selfT:
            for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
                nx, ny = ax + dx, ay + dy
                if (nx, ny) in oppT:
                    boundary.append((nx, ny))
        target_cells = boundary if boundary else list(oppT)

    def step_score(nx, ny):
        # discourage obstacles (engine keeps us if invalid, but still avoid when possible)
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**9
        gain = 0
        if (nx, ny) in oppT:
            gain += 18  # flipping on entry
        elif (nx, ny) not in selfT:
            gain += 8   # likely unclaimed / expansion
        # proximity: closer to good target is better; but stay somewhat away from opponent to avoid getting pinned
        best_t = None
        best_d = 10**9
        for (tx, ty) in target_cells:
            d = man(nx, ny, tx, ty)
            if d < best_d:
                best_d, best_t = d, (tx, ty)
        # edge fighting boost: unclaimed on edges tends to be high value in territory control
        edge_bonus = 0
        if best_t is not None:
            tx, ty = best_t
            if tx in (0, w - 1) or ty in (0, h - 1):
                edge_bonus = 6
        # keep somewhat toward opponent if we can flip; otherwise toward center for stability
        toward_opp = 6 - min(12, man(nx, ny, ox, oy) // 2)
        toward_center = 4 - min(8, man(nx, ny, w // 2, h // 2) // 2)
        # small penalty for moving away from self territory cluster
        near_self = 0
        if selfT:
            near_self = 2 - min(6, min(manhattan for manhattan in [man(nx, ny, ax, ay) for (ax, ay) in selfT[:5]]) // 2)
        return gain + (18 - best_d) + edge_bonus + toward_opp + toward_center + near_self

    # Deterministic tie-break: prefer higher score, then closer to target, then lexicographic move.
    best_move = (0, 0)
    best_val = -10**18
    best_dist = 10**9
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = step_score(nx, ny)
        dist = 0
        if unclaimed:
            # compute distance to closest unclaimed target for tie-break deterministically
            dist = min(man(nx, ny, tx, ty) for tx, ty in target_cells) if target_cells else 0
        if val > best_val or (val == best_val and dist < best_dist) or (val == best_val and dist == best_dist and (dx, dy) < best_move):
            best_val, best_dist, best_move = val, dist, (dx, dy)

    # If all moves invalid, stay still.
    return [int(best_move[0]), int(best_move[1])]