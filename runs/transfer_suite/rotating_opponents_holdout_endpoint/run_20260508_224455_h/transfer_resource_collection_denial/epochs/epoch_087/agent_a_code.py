def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = observation.get("resources") or []
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    if not resources:
        return [0, 0]

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    # Pick target that we can reach earlier than opponent; tie-break by proximity and coords.
    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles or not inb(rx, ry):
            continue
        md = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        # Higher is better: (od-md) first, then our distance smaller, then coords smaller
        key = (od - md, -md, -(rx + 9 * ry), -rx)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Score each move by resulting advantage and obstacle avoidance.
    chosen = (0, 0)
    chosen_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        hits = (nx, ny) in obstacles
        # If hits obstacle, engine keeps us at place; reflect that.
        ax, ay = (sx, sy) if hits else (nx, ny)
        our_d = dist8(ax, ay, tx, ty)
        opp_d = dist8(ox, oy, tx, ty)
        # Also slight preference for moving toward target and away from opponent being close to any resource.
        # Use best current resource distance to opponent for tie-break.
        min_opp_to_res = None
        for rr in resources:
            rx, ry = int(rr[0]), int(rr[1])
            if (rx, ry) in obstacles or not inb(rx, ry):
                continue
            d = dist8(ox, oy, rx, ry)
            if min_opp_to_res is None or d < min_opp_to_res:
                min_opp_to_res = d
        if min_opp_to_res is None:
            min_opp_to_res = 99
        # Higher key better
        key = (opp_d - our_d, -(our_d), -abs(ax - tx) - abs(ay - ty), -(abs(ax - ox) + abs(ay - oy)), -dx, -dy, hits)
        if chosen_key is None or key > chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]