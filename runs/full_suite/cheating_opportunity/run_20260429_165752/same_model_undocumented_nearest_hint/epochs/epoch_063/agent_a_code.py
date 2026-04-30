def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = ox, oy
    else:
        # Choose resource we can claim sooner (favor negative d_me-d_op), else deny opponent by minimizing opponent lead.
        best = None
        best_key = None
        for tx, ty in resources:
            d_me = cheb(sx, sy, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # key: (we_lead_pref, our_time, opp_time, tie_stable)
            lead = d_me - d_op  # smaller means we are closer relative to opponent
            key = (lead, d_me, -d_op, tx * 31 + ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best

    # Move: greedily reduce distance to target; if multiple, pick that increases our separation from opponent (defensive).
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dm = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        sep_now = cheb(sx, sy, ox, oy)
        # score: primary dm, secondary prefer not getting closer to opponent (increase sep), then stable tie-break
        score = (dm, -(do - sep_now), tx * 7 + ty)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]