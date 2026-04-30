def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        tx, ty = cx, cy
    else:
        # Target resource that we can reach earlier than opponent (maximize opp_dist - self_dist).
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer positive advantage; tie-break by closeness and centrality.
            key = (-(do - ds), ds, cheb(rx, ry, cx, cy), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best if best is not None else (cx, cy)

    # If opponent is significantly closer to the best target, try to "shadow" it by moving to an adjacent approach cell.
    # Otherwise just go for target.
    opp_on_target = 0
    if resources:
        ds0 = cheb(sx, sy, tx, ty)
        do0 = cheb(ox, oy, tx, ty)
        if do0 + 1 < ds0:
            opp_on_target = 1

    target_cells = [(tx, ty)]
    if opp_on_target:
        for dx, dy in moves:
            nx, ny = tx + dx, ty + dy
            if inb(nx, ny) and (nx, ny) not in occ:
                target_cells.append((nx, ny))

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        # Value: advantage at best target cell + centrality - slight separation penalty to avoid being outflanked.
        best_adv = None
        for cx2, cy2 in target_cells:
            ds = cheb(nx, ny, cx2, cy2)
            do = cheb(ox, oy, cx2, cy2)
            adv = do - ds  # higher means we are closer than opponent
            key = (-(adv), ds, cheb(cx2, cy2, cx, cy))
            if best_adv is None or key < best_adv:
                best_adv = (-(adv), ds, cheb(cx2, cy2, cx, cy), adv)
        adv = best_adv[3]
        val = (-(adv), cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy), nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]