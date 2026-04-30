def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Change targeting deterministically across epochs/turns:
    # early -> chase nearest; late -> secure a more distant resource line.
    t = int(observation.get("turn_index") or 0)
    late = t > 45 or (int(observation.get("remaining_resource_count") or len(resources) or 0) <= 4)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        if not resources:
            val = -man(nx, ny, ox, oy)  # just keep away
        else:
            # choose target resource deterministically for this move
            best_target_score = -10**18
            best_target_dist = 10**9
            for rx, ry in resources:
                d_me = man(nx, ny, rx, ry)
                d_op = man(ox, oy, rx, ry)
                # Prefer resources we can reach sooner; in late game also prefer maximizing remaining distance advantage.
                reach_gain = (d_op - d_me)
                if late:
                    # secure: bias toward farther resources but still only if we are competitive
                    val_t = 2 * reach_gain + 0.02 * (d_me + man(nx, ny, 0, h-1) + d_me)
                    if val_t > best_target_score or (val_t == best_target_score and d_me < best_target_dist):
                        best_target_score = val_t
                        best_target_dist = d_me
                else:
                    val_t = 2.5 * reach_gain - 0.01 * d_me
                    if val_t > best_target_score or (val_t == best_target_score and d_me < best_target_dist):
                        best_target_score = val_t
                        best_target_dist = d_me

            # obstacle-aware micro-bias: avoid stepping into tight corners by counting available neighbors
            neigh = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if inside(tx, ty):
                    neigh += 1

            # opponent pressure: if close, head toward contested targets (increase reach_gain effect by closeness)
            op_dist = man(nx, ny, ox, oy)
            contested = 1.0 / (1 + op_dist)
            val = best_target_score + 0.1 * neigh + 0.3 * contested

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]