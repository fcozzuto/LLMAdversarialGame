def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target where we are (or soon become) closer than opponent.
    best = None
    for x, y in resources:
        d_me = cheb(sx, sy, x, y)
        d_op = cheb(ox, oy, x, y)
        adv = d_op - d_me  # higher is better
        # Prefer larger advantage; then prefer closer to us; then closer to opponent (to deny); then coords.
        key = (-(adv), d_me, d_op, x, y)
        if best is None or key < best[0]:
            best = (key, (x, y), d_me, d_op, adv)

    _, (tx, ty), _, _, _ = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate move: progress to target and (slight) move to deny opponent.
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # If opponent is much closer, slightly bias towards blocking nearer resources by choosing move that reduces max(d_me - d_op).
        # Also add small penalty for moving away from current target direction.
        progress = d_me
        deny = max(0, d_op - d_me)
        # Tie-break deterministically by absolute move vector sum and position.
        key = (progress, -deny, abs(dx) + abs(dy), nx, ny)
        candidates.append((key, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]