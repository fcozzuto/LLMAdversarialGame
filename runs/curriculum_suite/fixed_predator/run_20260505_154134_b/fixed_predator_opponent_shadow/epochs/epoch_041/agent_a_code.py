def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def pick_target():
        if not resources:
            return None
        best = None
        best_key = None
        for cx, cy in resources:
            sd = cheb(sx, sy, cx, cy)
            od = cheb(ox, oy, cx, cy)
            # Prefer resources we can reach relatively sooner; tie-break by determinism.
            key = (sd - od, sd, cx, cy)
            if best_key is None or key < best_key:
                best_key = key
                best = (cx, cy)
        return best

    target = pick_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue
        obstacle_pen = -1000 if (nx, ny) in obs else 0
        new_sd = cheb(nx, ny, tx, ty)
        new_od = cheb(nx, ny, ox, oy)  # keep some distance from opponent while collecting
        opp_to_target = cheb(ox, oy, tx, ty)
        # Higher is better:
        # - reduce distance to target
        # - keep opponent farther from us
        # - consider our advantage vs opponent on the target
        advantage = (opp_to_target - new_sd)
        score = (advantage * 10) + (-new_sd * 3) + (new_od * 0.5) + obstacle_pen + (-(abs(nx - tx) + abs(ny - ty)) * 0.05)
        # Deterministic tie-breaking by move order and coordinates
        if best_score is None or score > best_score or (score == best_score and (dxm, dym) < tuple(best_move)):
            best_score = score
            best_move = [dxm, dym]

    return best_move