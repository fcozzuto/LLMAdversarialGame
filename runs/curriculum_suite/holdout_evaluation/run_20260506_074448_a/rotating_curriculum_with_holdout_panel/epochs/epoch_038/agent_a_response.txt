def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    def center_bias(x, y):
        cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
        dx, dy = x - cx0, y - cy0
        return -(dx * dx + dy * dy) * 0.005

    def best_opp_dist(nx_ox, nx_oy, tx, ty):
        bd = 10**9
        for dx, dy in deltas:
            ax, ay = nx_ox + dx, nx_oy + dy
            if inb(ax, ay) and (ax, ay) not in obstacles:
                bd = min(bd, man(ax, ay, tx, ty))
        return bd

    if not resources:
        # deterministic drift towards nearest edge corner lane
        edges = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(edges, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Choose a "steal/block" target: maximize (opp closer than me) advantage first, then proximity.
    def target_key(tx, ty):
        md = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        return (od - md, -md, -(abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2)), tx, ty)

    target = max(resources, key=lambda p: target_key(p[0], p[1]))
    tx, ty = target[0], target[1]

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            v = -10**15
        else:
            my_d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            # If opponent would be able to get to target in 1 move from their current position, penalize.
            opp_next_best = best_opp_dist(ox, oy, tx, ty)
            immediate_loss = 1 if opp_next_best <= 1 else 0
            v = (opp_d - my_d) * 2.0 - my_d * 0.25 + center_bias(nx, ny) - immediate_loss * 6.0

            # Also modestly prefer moves that move "along" towards target.
            if my_d < man(sx, sy, tx, ty):
                v += 0.6
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move