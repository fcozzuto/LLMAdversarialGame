def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def step_towards(tx, ty):
        if sx == tx and sy == ty:
            return 0, 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    best_win = None
    best_win_key = None
    best_comp = None
    best_comp_key = None

    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gap = od - sd
        # Candidate that we can reach earlier (win-like)
        if best_win is None or gap > best_win_key[0] or (gap == best_win_key[0] and sd < best_win_key[1]) or (
            gap == best_win_key[0] and sd == best_win_key[1] and (rx, ry) < (best_win_key[2], best_win_key[3])
        ):
            best_win = (rx, ry)
            best_win_key = (gap, sd, rx, ry)
        # Candidate that is most contested (opponent close)
        key = (od, sd, rx, ry)
        if best_comp is None or key < best_comp_key:
            best_comp = (rx, ry)
            best_comp_key = key

    target = best_win if best_win_key[0] > 0 else best_comp
    tx, ty = target

    dx, dy = step_towards(tx, ty)
    # Obstacle-aware: pick the best among allowed deltas that avoids obstacles.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (dx, dy)
    best_val = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer closer to target; break ties by favoring gap to opponent after move.
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        val = (ns, -(no - ns), abs((nx - tx)) + abs((ny - ty)), mx, my)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]