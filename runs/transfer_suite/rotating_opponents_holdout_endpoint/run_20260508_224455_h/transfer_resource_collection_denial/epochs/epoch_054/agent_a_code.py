def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((int(x), int(y)) for x, y in obstacles_list)
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    r += 1
        return r

    def score_for(rx, ry, selfd, opdd):
        adv = opdd - selfd  # positive if we are closer
        return 30 * adv - selfd - 4 * risk(rx, ry)

    # Estimate opponent's nearest "good" resource
    best_opp = None
    best_opp_val = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        v = score_for(rx, ry, do, ds)  # from opponent perspective
        if v > best_opp_val:
            best_opp_val = v
            best_opp = (int(rx), int(ry))
    opp_tx, opp_ty = best_opp

    # Choose target: prefer resources we can reach before opponent; else contest best opponent target
    best = None
    best_val = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        can_beat = ds <= do
        v = (100 if can_beat else 0) + score_for(rx, ry, ds, do)
        # Also add slight penalty if far from opponent's expected target (to keep pressure/interception)
        v -= 0.5 * cheb(rx, ry, opp_tx, opp_ty)
        if v > best_val:
            best_val = v
            best = (int(rx), int(ry))
    tx, ty = best

    # Move one step toward target, but avoid stepping adjacent to obstacles if possible
    best_move = [0, 0]
    best_move_val = -10**18
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dself = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, opp_tx, opp_ty)
        # If opponent is already closer to our target, prioritize moves that reduce dop (intercept pressure)
        ds_to_target = cheb(sx, sy, tx, ty)
        do_to_target = cheb(ox, oy, tx, ty)
        intercept = dop if do_to_target < ds_to_target else 0
        val = -dself + 0.6 * (cheb(ox, oy, tx, ty) - dself) - 3 * risk(nx, ny) - 0.15 * intercept
        if val > best_move_val:
            best_move_val = val
            best_move = [int(dx), int(dy)]

    return best_move