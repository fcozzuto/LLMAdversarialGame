def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]
    if not valid(sx, sy):
        sx, sy = 0, 0
    if not valid(ox, oy):
        ox, oy = max(0, min(w - 1, ox)), max(0, min(h - 1, oy))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Strategic target: maximize how much closer we are than opponent (or the best "catchable" alternative)
    best = None
    best_score = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer positive lead strongly; if no leads, pick the least bad based on smaller sd and larger od
        score = (od - sd) * 100 - sd
        if best_score is None or score > best_score or (score == best_score and (sd < best_sd)):
            best = (rx, ry)
            best_score = score
            best_sd = sd

    tx, ty = best

    # Local obstacle-aware step: move that most reduces distance to target; tie-break by reducing opponent reachability
    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                ds = cheb(nx, ny, tx, ty)
                new_oxd = cheb(ox, oy, tx, ty)
                # Estimate opponent progress only if we move in same general direction: small deterministic tie-break
                # (We can't move opponent, but we can bias against giving them a shortcut by choosing moves that also
                # reduce their distance to current target if they already are closer.)
                opp_ds = cheb(ox, oy, tx, ty)
                moves.append((ds, -opp_ds, dx, dy))
            else:
                # invalid moves are effectively rejected; skip
                pass
    if not moves:
        return [0, 0]
    moves.sort()
    return [int(moves[0][2]), int(moves[0][3])]