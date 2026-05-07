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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource where we are closest relative to opponent (maximize opp_dist - my_dist)
    best = resources[0]
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer us being closer; if tie, prefer smaller my distance; then larger opp distance.
        key = (d_op - d_me, -d_me, d_op, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Evaluate one-step moves with obstacle/bounds constraints.
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    # Deterministic order already, but tie-break by target progress then advantage.
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_me_next = cheb(nx, ny, tx, ty)
        d_me_now = cheb(sx, sy, tx, ty)
        d_op_target = cheb(ox, oy, tx, ty)
        adv_next = d_op_target - d_me_next

        # Higher is better: advance, then reduce distance to target, then slight preference for moving.
        score = (adv_next, -(d_me_next), (d_me_now - d_me_next), -abs(nx - tx) - abs(ny - ty), -abs(dx) - abs(dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]