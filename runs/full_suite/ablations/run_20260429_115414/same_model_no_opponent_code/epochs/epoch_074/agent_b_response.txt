def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            cur_best = -10**18
            for tx, ty in resources:
                ds = dist(nx, ny, sx, sy)  # small stabilization, deterministic
                d_self = dist(nx, ny, tx, ty)
                d_op = dist(ox, oy, tx, ty)
                # prioritize resources we can reach earlier than opponent; penalize self distance
                val = (d_op - d_self) * 1000 - d_self - ds * 0.1
                cur_best = val if val > cur_best else cur_best
            # small tie-break: prefer moving closer to opponent if can't secure any resource advantage
            tie = -(dist(nx, ny, ox, oy))
            val2 = cur_best + tie * 0.01
            if val2 > best_val:
                best_val = val2
                best_move = (dx, dy)
    else:
        # No visible resources: move toward center while not walking into obstacles; keep away from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            dc = abs(nx - cx) + abs(ny - cy)
            da = dist(nx, ny, ox, oy)
            val = -dc + da * 0.01
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]