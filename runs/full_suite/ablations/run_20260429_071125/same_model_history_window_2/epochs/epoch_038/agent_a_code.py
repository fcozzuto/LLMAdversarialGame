def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    obs_list = list(obstacles)

    def obstacle_penalty(x, y):
        p = 0
        for ax, ay in obs_list:
            d = cheb(x, y, ax, ay)
            if d == 0:
                return 10.0
            if d == 1:
                p += 1.0
            elif d == 2:
                p += 0.35
        return p

    # Evaluation from a hypothetical position: mix "race lead" and "risk-avoidance".
    def eval_pos(px, py):
        best_key = None
        for tx, ty in resources:
            ds = cheb(px, py, tx, ty)
            do = cheb(ox, oy, tx, ty)
            adv = do - ds
            # Late-game: focus more on denying by increasing weight on negative ds (closer to deny).
            late = observation.get("turn_index", 0) >= 28
            if late:
                key = (adv * 2.0 - ds * 0.9, -ds, -cheb(px, py, ox, oy), tx, ty)
            else:
                key = (adv * 1.6 - ds * 0.25, -ds, -cheb(px, py, ox, oy), tx, ty)
            if best_key is None or key > best_key:
                best_key = key
        return best_key[0] - 0.15 * obstacle_penalty(px, py)

    deltas = (-1, 0, 1)
    best = None
    best_move = [0, 0]
    for dx in deltas:
        for dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = eval_pos(nx, ny)
            # Small deterministic tie-break: prefer moves that keep option space (less distance to opponent).
            t = (val, -cheb(nx, ny, ox, oy), -cheb(nx, ny, sx, sy), dx, dy)
            if best is None or t > best:
                best = t
                best_move = [int(dx), int(dy)]
    return best_move