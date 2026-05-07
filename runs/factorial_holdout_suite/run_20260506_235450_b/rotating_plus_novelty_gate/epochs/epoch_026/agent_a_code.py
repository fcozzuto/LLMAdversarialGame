def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_adv(px, py):
        # Higher is better: be closer than opponent, then be close.
        best = -10**9
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = (od - sd)
            # Encourage immediate pickup and "race win" states
            score = adv * 100 + (1000 if sd == 0 else 0) - sd
            if score > best:
                best = score
        return best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        val = best_adv(nx, ny)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move