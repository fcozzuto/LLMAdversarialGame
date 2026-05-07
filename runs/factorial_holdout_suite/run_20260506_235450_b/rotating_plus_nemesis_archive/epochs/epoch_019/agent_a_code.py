def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]
    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a resource we can reach strictly before opponent; otherwise, maximize advantage
    best = None  # tuple for comparison
    for r in resources:
        tx, ty = r[0], r[1]
        if (tx, ty) in obstacles:
            continue
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        if sd == 0:
            best = (1, -10**9, 0, -od)  # already handled, but keep deterministic
            break
        can_win = 1 if sd < od else 0
        # Prefer: can_win, then smaller sd, then larger (od-sd), then lexicographic resource position
        adv = od - sd
        cand = (can_win, -sd, -adv, tx, ty)
        if best is None or cand > best:
            best = cand
            best_t = (tx, ty, sd, od)

    tx, ty, sd, od = best_t

    # Move one step toward target, avoiding obstacles; deterministic direction priority
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        nod = cheb(nx, ny, ox, oy)  # mild safety term to reduce edge-clumping
        # Prefer decreasing distance; if tied, prefer increasing opponent distance relative to our progress
        progress = sd - nd
        opp_adv = cheb(ox, oy, tx, ty) - nd
        cand_score = progress * 1000 + opp_adv * 10 - nod * 0.01
        if cand_score > best_score:
            best_score = cand_score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]