def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def best_target():
        if not resources:
            return None
        best = None
        best_val = -10**18
        for (rx, ry) in resources:
            d_me = man(sx, sy, rx, ry)
            d_op = man(ox, oy, rx, ry)
            # Strongly prefer targets where we are earlier; otherwise still move toward closer ones.
            if d_me <= d_op:
                val = (d_op - d_me + 1) * 10000 - d_me
            else:
                val = -(d_me * 50 + (d_me - d_op) * 200) - (rx * 3 + ry)
            if val > best_val:
                best_val = val
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = 10**18
    # Greedy step: avoid obstacles/out-of-bounds, minimize our distance to target; tie-break by maximizing race advantage.
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_new = man(nx, ny, tx, ty)
        d_op = man(ox, oy, tx, ty)
        # score tuple simulated by a single number: primary minimize d_new, secondary maximize advantage, tertiary deterministic.
        advantage = d_op - d_new
        score = d_new * 100000 - advantage * 1000 + (ny * w + nx)
        if score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    dx, dy = best
    return [int(dx), int(dy)]