def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < grid_w and 0 <= y < grid_h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick target deterministically:
    # Prefer a resource closer to self than opponent; among those, minimize self distance.
    # Otherwise, choose a resource that maximizes the gap (opp_dist - self_dist).
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = ((sd <= od), (sd if sd <= od else -(od - sd)), (rx, ry))
        # Normalize to a comparable tuple: earlier in tuple is better
        # For sd<=od: best when sd minimal; for else: best when gap (od-sd) maximal => -(od-sd) minimal.
        score = (0 if sd <= od else 1, sd if sd <= od else -(od - sd), rx, ry)
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    # Evaluate candidate moves (8-neighborhood + stay), avoid obstacles/outside.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp_to_target = cheb(ox, oy, tx, ty)
        # Prefer decreasing distance to target and (if tied) being further from opponent.
        # Also slightly prefer not staying.
        key = (d_self, cheb(nx, ny, ox, oy), dx == 0 and dy == 0, d_opp_to_target)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is not None:
        return best_move

    return [0, 0]