def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Deny-then-collect: prefer resources where we're at least as close as opponent;
    # if none, go to the resource where we can "catch up" soonest.
    best = None
    best_score = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Primary: advantage (d_op - d_me). Secondary: closeness. Tertiary: bias away from opponent.
        advantage = d_op - d_me
        sep = cheb(sx, sy, ox, oy)
        score = (advantage, -d_me, sep)
        if best is None or score > best_score:
            best = (rx, ry)
            best_score = score

    tx, ty = best
    # Take one step toward target while avoiding obstacles; break ties by maximizing separation from opponent.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                d_new = cheb(nx, ny, tx, ty)
                d_op_new = cheb(nx, ny, ox, oy)
                # Prefer smaller distance to target; then larger distance from opponent.
                candidates.append((d_new, -d_op_new, dx, dy))
    candidates.sort()
    if not candidates:
        return [0, 0]
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]