def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(a, b, c, d): 
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy
    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            val = -d2(nx, ny, cx, cy)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]
    # Two-phase: earlier compete for closest, later (fewer resources) switch to advantage-gap.
    rem = observation.get("remaining_resource_count", len(resources))
    competitive = rem <= 6
    best_score = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_best = -10**18
        opp_best = -10**18
        for rx, ry in resources:
            mydist = d2(nx, ny, rx, ry)
            oppdist = d2(ox, oy, rx, ry)
            # Avoid getting "too close" to an obstacle-adjacent resource is implicit via legality; keep attraction smooth.
            if competitive:
                gap = (oppdist - mydist)
                if gap > my_best: my_best = gap
            else:
                # Prefer minimizing our distance; if opponent is closer, still compete but less aggressively.
                val = -mydist - 0.3 * max(0, mydist - oppdist)
                if val > my_best: my_best = val
        # Center bias to reduce tie-stalemates
        center_bias = -0.02 * d2(nx, ny, cx, cy)
        # Small repulsion from opponent to prevent being blocked by them
        opp_rep = -0.005 * d2(nx, ny, ox, oy)
        # If competitive, normalize rough scale by also including our closeness
        if competitive:
            # Estimate closeness from my_best using nearest resource distance
            closest = None
            for rx, ry in resources:
                md = d2(nx, ny, rx, ry)
                if closest is None or md < closest: closest = md
            closeness_term = -0.001 * closest
            score = my_best + center_bias + opp_rep + closeness_term
        else:
            score = my_best + center_bias + opp_rep
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    if best_score is None:
        return [0, 0]
    return [best_move[0], best_move[1]]