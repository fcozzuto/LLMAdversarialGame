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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Try to take resources where we are closer than opponent; else deny by approaching them from the other side.
    best = (0, 0)
    best_val = -10**18

    def eval_at(tx, ty, nx, ny):
        d_me = manh(nx, ny, tx, ty)
        d_op = manh(ox, oy, tx, ty)
        if d_me == 0:
            return 10**7
        # Advantage when we are closer (or will be), penalize if opponent is clearly closer.
        adv = d_op - d_me
        # Prefer nearer targets overall, and avoid moving away from own improvement.
        center = abs(tx - (w - 1) / 2.0) + abs(ty - (h - 1) / 2.0)
        return adv * 1000 - d_me * 10 - center * 1

    # If resources exist, evaluate each move by best target value; then add small steering away from obstacles.
    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = -10**18
            for rx, ry in resources:
                val = max(val, eval_at(rx, ry, nx, ny))
            # Obstacle pressure: small penalty if too close to obstacles to avoid getting stuck.
            near_obs = 0
            for ox1, oy1 in obstacles:
                if abs(ox1 - nx) <= 1 and abs(oy1 - ny) <= 1:
                    near_obs += 1
            val -= near_obs * 3
            # Tie-break deterministically: prefer moves that reduce distance to opponent slightly when no clear advantage.
            val -= manh(nx, ny, ox, oy) * 0.001
            if val > best_val:
                best_val = val
                best = (dx, dy)
    else:
        # No resources: move toward the midpoint of the two agents to contest future paths; keep obstacle-safe.
        mx = int((sx + ox) / 2)
        my = int((sy + oy) / 2)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = -manh(nx, ny, mx, my) * 10
            near_obs = 0
            for ox1, oy1 in obstacles:
                if abs(ox1 - nx) <= 1 and abs(oy1 - ny) <= 1:
                    near_obs += 1
            val -= near_obs * 3
            if val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]