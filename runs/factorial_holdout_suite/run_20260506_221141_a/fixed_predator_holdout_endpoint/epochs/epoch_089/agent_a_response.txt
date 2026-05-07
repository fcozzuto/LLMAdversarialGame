def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Resource choice: deny when opponent is closer; otherwise push our advantage.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # If we are closer, prioritize largest lead; if not, prioritize smallest contest gap (closest denial).
        lead = od - sd
        # Also slightly prefer nearer goals to reduce wandering.
        key = (1 if lead > 0 else 0, abs(lead), -min(sd, od))
        if best is None or key > best_key or (key == best_key and (rx, ry) < best):
            best_key = key
            best = (rx, ry)

    tx, ty = best

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Prefer moves that reduce Chebyshev distance to target; if tie, prefer moves that increase distance from opponent.
    base_dx, base_dy = sign(tx - sx), sign(ty - sy)
    preferred = (base_dx, base_dy)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cur_dist = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        odist = cheb(nx, ny, ox, oy)
        mkey = (-1 if (dx, dy) == preferred else 0, -(nd - cur_dist), odist, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]