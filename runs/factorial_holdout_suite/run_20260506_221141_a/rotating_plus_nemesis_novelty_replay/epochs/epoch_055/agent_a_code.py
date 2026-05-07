def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs_set:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs_set:
            legal.append((dx, dy))

    # Choose a resource where we lead by the largest margin; otherwise pick closest to us.
    best = None  # (lead, self_d, -opp_d, tx, ty)
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd
        cand = (lead, -sd, -od, rx, ry)  # deterministic ordering: higher lead first, then smaller sd
        if best is None or cand > best:
            best = cand

    _, nsd, nod, tx, ty = best
    # Move that most reduces our distance to target, with tie-break against opponent proximity.
    best_move = None  # (self_next_d, opp_next_d, dx, dy)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(nx, ny, ox, oy)
        cand = (self_d, opp_d, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand

    return [int(best_move[2]), int(best_move[3])]