def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # Fallback: stay near our corner/home while keeping distance from opponent path-cuts
    if not resources:
        tx, ty = 0, h - 1
        bx, by = w - 1, 0
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy) * 200 - (abs(nx - tx) + abs(ny - ty)) * 2 + cheb(nx, ny, bx, by) * 1
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Choose target: maximize "denial pressure" (we arrive earlier) with a tie-break to grab closer cells.
    best_res = resources[0]
    best_gain = -10**18
    for rx, ry in resources:
        d_ours = cheb(x, y, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        gain = (d_opp - d_ours) * 1000 - d_ours * 2 + (d_opp == d_ours) * 30
        # If resources are scarce, slightly prioritize nearer ones for faster accrual.
        if len(resources) <= 3:
            gain += (18 - d_ours) * 2
        if gain > best_gain:
            best_gain = gain; best_res = [rx, ry]

    rx, ry = best_res

    # One-step lookahead: pick legal move that improves denial to target and reduces opponent ability to contest.
    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        d_self = cheb(nx, ny, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)

        # Encourage reaching the target sooner than opponent; discourage letting opponent be "equal/earlier".
        v = (d_opp - d_self) * 1200 - d_self * 6

        # Light obstacle/trajectory guidance: prefer moves that keep us from getting closer to a "nearby" opponent.
        v += cheb(nx, ny, ox, oy) * 2

        # If our move hits/approaches a resource cell, bump it.
        if any(r[0] == nx and r[1] == ny for r in resources):
            v += 500

        if v > bestv:
            bestv = v; best = [dx, dy]

    return best