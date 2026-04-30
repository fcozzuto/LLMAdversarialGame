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

    rem = observation.get("remaining_resource_count")
    try:
        rem = int(rem or 0)
    except:
        rem = 0
    late = rem <= 3

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        targets = resources
    else:
        targets = [(ox, oy)]

    best_move = (0, 0)
    best_score = -10**18

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        total = -cheb(nx, ny, ox, oy) * 0.05  # slight separation
        for tx, ty in targets:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            d_cur_self = cheb(sx, sy, tx, ty)
            closer_bonus = 0.25 if d_self < d_cur_self else 0.0
            block_penalty = 1.4 if d_opp <= d_cur_self else 0.0
            if late:
                # late game: aggressively secure nearer resources
                score = -d_self + 0.35 * d_opp - block_penalty + closer_bonus * 2.0
            else:
                score = -0.9 * d_self + 0.25 * d_opp - block_penalty + closer_bonus
            total = score if score > total else total
        if total > best_score or (total == best_score and (ddx, ddy) < best_move):
            best_score = total
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]