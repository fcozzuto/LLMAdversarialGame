def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(a, b, c, d):
        dx = a - c; dy = b - d
        return dx * dx + dy * dy
    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        # Prefer resources we can reach earlier than opponent (advantage)
        for rx, ry in resources:
            ds = dist2(sx, sy, rx, ry)
            do = dist2(ox, oy, rx, ry)
            adv = do - ds  # larger means we are closer
            if best is None or adv > best[0] or (adv == best[0] and (ds < best[1] or (ds == best[1] and (rx, ry) < best[2]))):
                best = (adv, ds, (rx, ry))
        tx, ty = best[2]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_target = dist2(nx, ny, tx, ty)
        d_opp = dist2(nx, ny, ox, oy)
        # Encourage closing on target while keeping some distance from opponent
        near_obs = 0
        for ax, ay in obstacles:
            if abs(ax - nx) <= 1 and abs(ay - ny) <= 1:
                near_obs += 1
        val = (-d_target) + 0.02 * d_opp - 0.5 * near_obs
        if bestm is None or val > bestm[0] or (val == bestm[0] and (dx, dy) < bestm[1]):
            bestm = (val, (dx, dy))
    if bestm is None:
        return [0, 0]
    dx, dy = bestm[1]
    return [dx, dy]