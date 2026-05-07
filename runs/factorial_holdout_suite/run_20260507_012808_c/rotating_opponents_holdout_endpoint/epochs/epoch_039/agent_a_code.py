def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        our_best = 10**9
        opp_best = 10**9
        best_gap = -10**9
        for rx, ry in resources:
            d_our = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_our < our_best: our_best = d_our
            if d_opp < opp_best: opp_best = d_opp
            gap = d_opp - d_our
            if gap > best_gap: best_gap = gap

        close_to_us = cheb(nx, ny, ox, oy)
        row_sync = abs(ny - oy)  # smaller means opponent can "sweep" toward us
        # Higher is better: prioritize reachable advantage, then staying far from opponent,
        # and lastly making progress to the nearest resource.
        val = (best_gap * 1000) - (our_best * 20) - (close_to_us * 8) - (max(0, 2 - row_sync) * 15)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]