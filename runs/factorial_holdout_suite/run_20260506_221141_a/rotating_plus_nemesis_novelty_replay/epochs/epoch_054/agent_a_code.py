def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
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

    ox, oy = observation.get("opponent_position", (0, 0))
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (score, -self_d, -opp_d, rx, ry, dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obs_set:
            continue
        best_for_move = None
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer moves that reduce our distance and/or increase relative pressure vs opponent.
            # Deterministic tie-break: fewer steps to resource, then closer to opponent? then lexicographic resource.
            score = (opp_d - self_d, -self_d, -opp_d, rx, ry)
            if best_for_move is None or score > best_for_move[0]:
                best_for_move = (score, self_d, opp_d)
        if best_for_move is None:
            continue
        score, self_d, opp_d = best_for_move
        cand = (score[0], score[1], score[2], score[3], score[4], dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[5]), int(best[6])] if best is not None else [0, 0]