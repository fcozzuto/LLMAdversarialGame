def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def best_resource_for(posx, posy):
        best = None
        best_key = None
        for rx, ry in resources:
            d_me = cheb(posx, posy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources where we're closer than opponent; tie-break by smaller our dist, then coords.
            key = (d_me - d_op, d_me, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_resource_for(sx, sy)
    if target is None:
        target = (w // 2, h // 2)

    tx, ty = target

    # Also consider an "escape" direction when opponent is very close: maximize distance slightly.
    opp_dist = cheb(sx, sy, ox, oy)
    prefer_op_away = 1.0 if opp_dist <= 2 else 0.35

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)

        # Resource contention: if opponent could grab target sooner, bias strongly away from it.
        d_me_cur = cheb(sx, sy, tx, ty)
        d_op_target = cheb(ox, oy, tx, ty)
        contention = -1.5 if d_me_cur > d_op_target else 0.0

        # Encourage progress: smaller distance is better.
        progress = -d_to_target

        # Light penalty for moving toward walls/corners only when not needed.
        wall_pen = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            wall_pen = 0.15

        # If a resource is exactly on the next cell, prioritize it.
        on_res = 1.0 if (nx, ny) in obstacles else 0.0  # obstacles are invalid, but keep deterministic
        on_resource = 1.0 if (nx, ny) == (tx, ty) else 0.0

        score = progress + prefer_op_away * (0.15 * d_to_opp) + contention + on_resource - wall_pen - on_res

        # Deterministic tie-break by fixed move order: use best_move index.
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]