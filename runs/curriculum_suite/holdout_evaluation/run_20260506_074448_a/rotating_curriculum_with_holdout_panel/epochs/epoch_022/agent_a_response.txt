def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            cx = nx if w == 1 else min(nx, w - 1 - nx)
            cy = ny if h == 1 else min(ny, h - 1 - ny)
            sc = cx + cy
            if sc > best[1]:
                best = ((dx, dy), sc)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    opp_nearest_dist = 10**9
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < opp_nearest_dist:
            opp_nearest_dist = d

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # pick a target resource that we can "steal" from opponent's current best
        best_target_val = -10**18
        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # if opponent's nearest is that resource, opp_d == opp_nearest_dist; otherwise opp_d > it.
            steal_bonus = (opp_d - opp_nearest_dist)  # positive when opponent is not currently focused there
            # prefer being closer than we are normally, but strongly prefer steal_bonus > 0 targets
            val = steal_bonus * 8 - our_d * 2
            if val > best_target_val:
                best_target_val = val

        # add a small tie-breaker: keep away from obstacles by preferring lower "blockedness"
        blockedness = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if not inb(tx, ty) or (tx, ty) in obstacles:
                blockedness += 1
        final_val = best_target_val - blockedness * 0.1 - (man(nx, ny, ox, oy)) * 0.05

        if final_val > best_val:
            best_val = final_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]