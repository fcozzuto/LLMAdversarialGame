def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    oxs = set((p[0], p[1]) for p in obstacles)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy
    if not resources:
        best = [0, 0]
        bestd = 10**9
        for dx, dy in ((0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in oxs:
                continue
            d = man(nx, ny, ox, oy)
            if d < bestd:
                bestd = d
                best = [dx, dy]
        return best
    # Choose a resource that we can secure before opponent, with distance-to-opponent bias
    best_res = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in oxs:
            continue
        d_self = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        # Prefer resources where we are not slower; otherwise still take if far enough from opponent
        # Add slight preference for mid-to-endgame progress by weighting with remaining_resource_count deterministically.
        remaining = observation.get("remaining_resource_count", len(resources))
        urgency = 1.0 + (12 - remaining) * 0.05
        lead = d_opp - d_self
        # Higher is better
        score = (lead * 10.0) + (-d_self * 2.0) + (-abs(3.5 - rx) * 0.1) + (-abs(3.5 - ry) * 0.1)
        score *= urgency
        # Deterministic tie-break: smaller (d_self, rx, ry)
        if score > best_score:
            best_score = score
            best_res = [rx, ry]
        elif score == best_score:
            if (d_self, rx, ry) < (man(sx, sy, best_res[0], best_res[1]), best_res[0], best_res[1]):
                best_res = [rx, ry]
    tx, ty = best_res
    # Move one step toward target; avoid obstacles; deterministic selection among candidates
    deltas = [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)
    # Candidate ordering: try exact desired step first, then others by resulting distance to target
    ordered = []
    for dx, dy in deltas:
        if dx == desired_dx and dy == desired_dy:
            ordered.append((dx, dy))
    for dx, dy in deltas:
        if (dx, dy) not in ordered:
            ordered.append((dx, dy))
    best = [0, 0]
    best_val = 10**18
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in oxs:
            continue
        d_t = man(nx, ny, tx, ty)
        # Extra bias: if we can't beat opponent to this target, at least move to reduce opponent's approach by staying away from them
        d_o = man(nx, ny, ox, oy)
        val = d_t * 5 - d_o  # smaller is better; prioritizes closeness to target, but keeps distance from opponent
        if val < best_val:
            best_val = val
            best = [dx, dy]
    return [int(best[0]), int(best[1])]