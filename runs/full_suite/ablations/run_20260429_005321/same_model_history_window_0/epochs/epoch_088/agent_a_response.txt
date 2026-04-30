def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = observation["obstacles"] or []
    obs_set = set((x, y) for x, y in obstacles)
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    # Choose best target resource to maximize being closer than opponent
    best = None
    best_adv = -10**9
    best_ds = 10**9
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and (rx+ry) < (best[0]+best[1] if best else 10**9)))):
            best_adv = adv
            best_ds = ds
            best = (rx, ry)
    if best is None:
        best = (w//2, h//2)
    tx, ty = best
    # Pick move that approaches target while avoiding obstacles when possible
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Encourage denying: move to reduce opponent advantage if possible
        opp_d = cheb(ox, oy, tx, ty)
        # If we move, our distance becomes nd, so advantage becomes opp_d - nd
        val = (opp_d - nd) * 1000 - nd
        # Small tie-break: prefer staying closer to center and away from borders
        cx, cy = w//2, h//2
        dist_center = cheb(nx, ny, cx, cy)
        val -= dist_center
        # Prefer not letting opponent immediately step onto same square by approximating
        if cheb(nx, ny, ox, oy) <= 1:
            val -= 5
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]