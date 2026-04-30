def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if (x, y) not in obstacles]
    if not res:
        best = max(legal, key=lambda t: cheb(t[2], t[3], ox, oy))
        return [best[0], best[1]]

    # Precompute opponent best after one move for each resource (ignoring our effect).
    opp_after = {}
    for rx, ry in res:
        best_od = 10**9
        for ddx, ddy in deltas:
            nx, ny = ox + ddx, oy + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = cheb(nx, ny, rx, ry)
                if d < best_od: best_od = d
        opp_after[(rx, ry)] = best_od if best_od < 10**9 else cheb(ox, oy, rx, ry)

    def move_score(nx, ny):
        best_lead = -10**9
        best_opp_race = 10**9
        closest = 10**9
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            od = opp_after[(rx, ry)]
            lead = od - myd  # positive means we are ahead
            if lead > best_lead: best_lead = lead
            if od - myd < best_opp_race: best_opp_race = od - myd
            if myd < closest: closest = myd
        # If we can secure something clearly earlier, prioritize it strongly.
        secure_bonus = 0
        if best_lead >= 2:
            secure_bonus = 50 + 5 * best_lead
        # Otherwise, deny: try to maximize the worst-case lead and also reduce distance to the closest pick.
        return secure_bonus + 8 * best_lead + 3 * best_opp_race - 1.5 * closest

    best_move = None
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        v = move_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]