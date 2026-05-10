def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role", "pursuer") or "pursuer").lower()
    pursuer = role != "evader"

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose a target for evader; pursuer targets the opponent position.
    if pursuer:
        tx, ty = ox, oy
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_corner = corners[0]
        best_d = -1
        for cx, cy in corners:
            d = cheb(cx, cy, ox, oy)
            if d > best_d:
                best_d = d
                best_corner = (cx, cy)
        tx, ty = best_corner

    best_move = [0, 0]
    best_score = None

    # Deterministic move ordering: iterate in fixed order; tie-break by first encountered.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) != (sx, sy) and not free(nx, ny):
            continue

        dist_to_op = cheb(nx, ny, ox, oy)
        dist_to_tgt = cheb(nx, ny, tx, ty)

        # Pursuer: minimize distance to opponent; Evader: maximize distance to opponent,
        # with a secondary push toward selected corner for consistent evasion.
        score = (dist_to_op, -dist_to_tgt) if pursuer else (dist_to_op, dist_to_tgt)
        if best_score is None:
            best_score = score
            best_move = [dx, dy]
        else:
            # For pursuer smaller dist_to_op is better; for evader larger dist_to_op is better.
            if pursuer:
                if score[0] < best_score[0] or (score[0] == best_score[0] and score[1] > best_score[1]):
                    best_score = score
                    best_move = [dx, dy]
            else:
                if score[0] > best_score[0] or (score[0] == best_score[0] and score[1] > best_score[1]):
                    best_score = score
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]