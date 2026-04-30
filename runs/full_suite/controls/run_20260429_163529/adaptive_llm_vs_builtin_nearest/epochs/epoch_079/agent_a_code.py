def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a resource we can reach before the opponent; otherwise pick one to contest.
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # score: prefer first arrival; then closer; then slight center bias
        first_bonus = 1000 if sd < od else (0 if sd == od else -1000)
        center_bias = - (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.01
        val = first_bonus + (od - sd) * 10 - sd + center_bias
        if best is None or val > best[0] or (val == best[0] and (sd < best[1] or (sd == best[1] and (rx, ry) < best[2]))):
            best = (val, sd, (rx, ry))
    target = best[2]
    tx, ty = target

    # Choose move delta that (1) heads to target, (2) keeps away from opponent, (3) avoids obstacles/out of bounds.
    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: 
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(nx, ny, ox, oy)
        # move score: primarily reduce distance to target, then increase opponent distance, slight tie to stay.
        sc = -nsd * 100 + nod * 2 - (1 if (dx == 0 and dy == 0) else 0) * 0.1
        if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]