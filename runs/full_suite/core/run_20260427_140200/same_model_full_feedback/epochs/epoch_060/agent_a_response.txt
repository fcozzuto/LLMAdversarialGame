def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Fallback: move to maximize distance from opponent (avoid easy steals), else stay.
        best_move = [0, 0]
        best_val = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    # Strategic change: choose move that maximizes advantage on the resource we can secure earliest,
    # also discouraging stepping into positions that reduce our lead vs opponent.
    cur_op_dist = cheb(sx, sy, ox, oy)
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate by best resource target under "lead" metric.
        best_target_val = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; penalize being behind.
            lead = d_op - d_me
            # Tie-break: prefer nearer resource and also positions that don't give opponent advantage.
            val = lead * 1000 - d_me * 3 - max(0, d_me - d_op) * 25
            if val > best_target_val:
                best_target_val = val

        # Additional shaping: don't move into a cell that makes opponent effectively closer than before.
        new_op_dist = cheb(nx, ny, ox, oy)
        opp_pressure = (cur_op_dist - new_op_dist)  # positive if we get closer to opponent
        val_total = best_target_val - opp_pressure * 40

        if val_total > best_val:
            best_val = val_total
            best_move = [dx, dy]

    return best_move