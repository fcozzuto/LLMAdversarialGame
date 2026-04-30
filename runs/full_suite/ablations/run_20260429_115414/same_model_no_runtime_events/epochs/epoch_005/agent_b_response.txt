def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(a, b):
        dx = a[0] - b[0]; dx = dx if dx >= 0 else -dx
        dy = a[1] - b[1]; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def best_step(pos, target):
        px, py = pos
        best = None
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if not ok(nx, ny): 
                continue
            t = cheb((nx, ny), target)
            # deterministic tie-break: prefer lexicographically smallest (dx,dy) among equals via ordering in deltas
            if best is None or t < best[0]:
                best = (t, dx, dy)
        if best is None:
            return (cheb(pos, target), 0, 0)
        return best
    sd = (sx, sy); od = (ox, oy)
    # Choose a target, then simulate both agents' next steps towards it; maximize our lead after response.
    best_key = None
    best_move = (0, 0)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        t = (rx, ry)
        our_t, our_dx, our_dy = best_step(sd, t)
        opp_t, opp_dx, opp_dy = best_step(od, t)
        # after our move, opponent responds by moving toward same target
        my_final = our_t
        opp_final = opp_t
        lead = opp_final - my_final
        # add secondary objective: if leads tie, prefer moving closer and deprioritize targets far from us initially
        key = (lead, -my_final, -abs(rx - sx) - abs(ry - sy), -((rx * 37 + ry * 17) % 1000003))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (our_dx, our_dy)
    dx, dy = best_move
    return [int(dx), int(dy)]