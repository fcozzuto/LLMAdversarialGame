def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in ob
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    # Choose best target by "race advantage": opp_dist - my_dist (prefer denying/stealing)
    tx, ty = sx, sy
    best_adv = None
    best_d = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        myd = md(sx, sy, rx, ry)
        oppd = md(ox, oy, rx, ry)
        adv = oppd - myd
        if best_adv is None or adv > best_adv or (adv == best_adv and (best_d is None or myd < best_d)):
            best_adv = adv
            best_d = myd
            tx, ty = rx, ry

    # If no resources or all invalid, just move toward center/opponent slightly
    if (not resources) or (best_adv is None):
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy

    # Evaluate one-step moves deterministically
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        # Encourage getting closer; also add mild pressure to keep opponent far from our target.
        oppd = md(ox, oy, tx, ty)
        # Slight tie-break: prefer moves that reduce distance to opponent (denier pressure) when adv is poor.
        my_to_opp = md(nx, ny, ox, oy)
        score = -myd
        if best_adv is not None and best_adv < 0:
            score += -0.05 * my_to_opp
        score += 0.02 * oppd

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]