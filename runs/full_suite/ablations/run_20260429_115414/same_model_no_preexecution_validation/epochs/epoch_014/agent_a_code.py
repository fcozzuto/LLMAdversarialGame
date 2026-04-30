def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        try:
            px, py = int(p[0]), int(p[1])
            obs_set.add((px, py))
        except:
            pass

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y): return inb(x, y) and (x, y) not in obs_set

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_target = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obs_set:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer than opponent; break ties toward smaller sd.
        key = (od - sd, -sd, -(rx * 9 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Contention: if opponent is close to the target, bias away a bit.
    my_to_t = cheb(sx, sy, tx, ty)
    op_to_t = cheb(ox, oy, tx, ty)
    contested = 1 if op_to_t <= my_to_t else 0

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist_t = cheb(nx, ny, tx, ty)
        dist_o = cheb(nx, ny, ox, oy)
        # Primary: get closer to target; Secondary: avoid opponent more when contested; Tertiary: reduce distance to us staying.
        val = (-dist_t, (dist_o if contested else dist_o // 2), -cheb(nx, ny, sx, sy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]