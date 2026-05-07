def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): 
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx + dy
    def nearest_obs_pen(x, y):
        # Penalize being adjacent to obstacles to avoid "move hits obstacle" traps.
        pen = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
            nx, ny = x + ax, y + ay
            if (nx, ny) in obstacles: pen += 2
        return pen

    if not resources:
        # Deterministic: head toward center while keeping away from obstacles.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]; bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            v = -(md(nx, ny, tx, ty)) - nearest_obs_pen(nx, ny)
            if v > bestv: bestv = v; best = [dx, dy]
        return best

    # Competitive interception: prefer moves that increase our lead to the best target,
    # but also reduce opponent's advantage on that same target.
    best = [0, 0]; bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: continue

        # Evaluate against each resource and take the best "overall" for us.
        local_best = -10**18
        for rx, ry in resources:
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)

            # Estimate opponent's next step improvement: assume they move toward resource.
            # This is heuristic but deterministic and cheap.
            best_opp_after = d_opp
            for odx, ody in moves:
                tx2, ty2 = ox + odx, oy + ody
                if not inb(tx2, ty2) or (tx2, ty2) in obstacles: 
                    continue
                best_opp_after = min(best_opp_after, md(tx2, ty2, rx, ry))

            # Our value: become closer, and make it harder for opponent to become closer.
            # Big weight on lead; smaller weight on absolute progress.
            lead_before = d_opp - md(sx, sy, rx, ry)
            lead_after = d_opp - d_self
            v = 5 * (lead_after - lead_before) + (-(d_self)) + (best_opp_after - d_opp) * 2

            # Extra tie-break: if we can land on it now, always take.
            if d_self == 0: v += 10**6
            if v > local_best: local_best = v

        v = local_best - nearest_obs_pen(nx, ny)
        if v > bestv: bestv = v; best = [dx, dy]
    return best