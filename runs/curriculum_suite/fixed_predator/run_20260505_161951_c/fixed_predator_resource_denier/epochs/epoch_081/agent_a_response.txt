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

    if not resources:
        tx, ty = w - 1, h - 1
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_goal = cheb(nx, ny, tx, ty)
            v = d_opp * 3 - d_goal
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    best = [0, 0]; bestv = -10**18
    # Evaluate our next position; pick move that maximizes contesting resources against opponent.
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        myd_opp = cheb(nx, ny, ox, oy)
        v = -myd_opp * 0.15  # don't drift into the opponent

        # For each resource, reward when we are (or will be) closer than opponent.
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if self_d == 0:
                v += 100000  # immediate capture
                continue
            # Contest value: how much nearer we are than opponent (or how much we close the gap).
            gap = opp_d - self_d
            # Also prefer moves that reduce our absolute distance even if still behind.
            v += gap * 50 - self_d * 2 - (0.25 * cheb(nx, ny, rx, ry))
            # Mildly penalize resources that are far for us and very close for opponent.
            if gap < 0:
                v += gap * 20

        # Tie-break deterministically: prefer moves that reduce our distance to nearest resource.
        if v > bestv + 1e-9:
            bestv = v; best = [dx, dy]
        elif abs(v - bestv) <= 1e-9:
            def nearest_dist(px, py):
                md = 10**9
                for rx, ry in resources:
                    d = cheb(px, py, rx, ry)
                    if d < md: md = d
                return md
            if nearest_dist(nx, ny) < nearest_dist(x + best[0], y + best[1]):
                best = [dx, dy]

    return best