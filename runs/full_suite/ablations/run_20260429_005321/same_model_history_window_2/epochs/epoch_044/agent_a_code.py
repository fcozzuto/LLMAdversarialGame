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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def best_adv_for(posx, posy):
        if not resources:
            return -cheb(posx, posy, ox, oy)
        best_key = None
        best_dme = None
        best_dop = None
        for rx, ry in resources:
            d_me = cheb(posx, posy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            key = d_op - d_me  # positive means we are closer (in turns) than opponent
            if best_key is None or key > best_key or (key == best_key and d_me < best_dme):
                best_key, best_dme, best_dop = key, d_me, d_op
        # break further ties by preferring resources where opponent is farther
        return (best_key, -(best_dop if best_dop is not None else 0), -(best_dme if best_dme is not None else 0))

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = best_adv_for(nx, ny)
        # add slight preference to reduce distance to chosen best resource via the same heuristic
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If something went wrong (all moves invalid), stay put.
    return [int(best_move[0]), int(best_move[1])]