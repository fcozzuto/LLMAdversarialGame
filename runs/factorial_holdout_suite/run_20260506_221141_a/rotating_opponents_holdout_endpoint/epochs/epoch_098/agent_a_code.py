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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def desir(x, y, target):
        tx, ty = target
        d_me = cheb(x, y, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Encourage collecting first: higher (d_op - d_me).
        # Tie-break to deny opponent: smaller d_op if possible.
        return (d_op - d_me) * 10000 - d_me * 10 - d_op

    # If multiple resources, aim for the one where we have the most tempo advantage.
    best_target = None
    best_key = None
    for r in resources:
        tx, ty = r
        d_me = cheb(sx, sy, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        adv = d_op - d_me
        key = (-adv, d_me, d_op, tx, ty)  # deterministic
        if best_key is None or key < best_key:
            best_key = key
            best_target = r

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tx, ty = best_target

    # Choose the move that maximizes our desirability toward the best target, with obstacle avoidance.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # If we can immediately collect, prioritize it strongly.
        immediate = 1 if (nx, ny) == (tx, ty) else 0
        val = immediate * 10**9 + desir(nx, ny, best_target)
        # Secondary tie-break: prefer reducing distance to the target (deterministic).
        if best_val is None or val > best_val or (val == best_val and (abs(tx - nx) + abs(ty - ny), dx, dy) < (abs(tx - (sx + best_move[0])) + abs(ty - (sy + best_move[1])), best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy)

    # If all moves blocked, stay.
    return [int(best_move[0]), int(best_move[1])]