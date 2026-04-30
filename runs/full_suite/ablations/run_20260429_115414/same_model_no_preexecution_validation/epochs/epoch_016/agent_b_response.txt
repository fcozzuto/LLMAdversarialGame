def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set
    if not resources:
        # simple obstacle-avoid + drift toward center while keeping away from opponent
        cx, cy = w // 2, h // 2
        best = None; bestv = None
        for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            v = cheb(nx, ny, cx, cy) - 0.3 * cheb(nx, ny, ox, oy)
            if bestv is None or v < bestv:
                bestv = v; best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    # Consider only resources likely to matter: closest few by our distance
    scored = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not legal(rx, ry): 
            continue
        d = cheb(sx, sy, rx, ry)
        scored.append((d, rx, ry))
    scored.sort(key=lambda t: t[0])
    cand_resources = scored[:6] if len(scored) > 6 else scored

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0); best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): 
            continue

        # Evaluate next state by choosing the best target for us, but penalize allowing opponent to be closer to that target.
        local_best = None
        for _, rx, ry in cand_resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            # If opponent is already closer, strongly discourage; otherwise race with a preference for earlier commitment.
            race = (od - sd)  # larger is better
            # Finish preference: smaller sd is better; also slightly prefer targets far from opponent to reduce contention.
            finish = -sd
            opp_far = cheb(ox, oy, rx, ry)
            # Obstacle/geometry proxy: prefer moves that improve "step toward target" (reduce cheb to target directly).
            step = cheb(sx, sy, rx, ry) - sd

            # Commitment: if opponent is within 1-2 steps, more aggressive blocking value.
            block = 0
            if od <= sd:
                block -= 20 + 2 * (sd - od)
            elif od - sd <= 2:
                block += 2 * (od - sd)

            val = 4.0 * race + 0.9 * finish + 0.03 * opp_far + 1.2 * step + block
            if local_best is None or val > local_best:
                local_best = val

        # Additional global safety: avoid squares that would be "too exposed" to opponent relative to our nearest resource
        # (deterministic, cheap).
        nearest_our = None
        for _, rx, ry in cand_resources:
            d = cheb(nx, ny, rx, ry)
            if nearest_our is None or d < nearest_our:
                nearest_our = d
        exposure = 0
        if nearest_our is not None:
            # exposure increases if opponent is closer to our nearest target than we are
            # approximate by comparing opponent distance to that nearest target
            for _, rx, ry in cand_resources:
                if cheb(nx, ny, rx, ry) == nearest_our:
                    exposure = cheb(ox, oy