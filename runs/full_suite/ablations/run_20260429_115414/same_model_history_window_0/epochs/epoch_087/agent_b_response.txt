def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d): return max(abs(a - c), abs(b - d))
    if resources:
        best_res = None
        best_val = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; also avoid ones opponent is much closer to
            val = sd - 0.35 * od + (0.02 * (sd + od))
            if best_val is None or val < best_val:
                best_val = val
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        # No resources: move to center-ish deterministically
        tx, ty = w // 2, h // 2

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def dist_new(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return 10**9
        return cheb(nx, ny, tx, ty)
    opp_close = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # Mild opponent avoidance when they are near
        opp_d = cheb(nx, ny, ox, oy)
        score = d * 10
        score -= 0.15 * opp_d
        # If opponent is very close, slightly increase spacing
        if opp_close <= 2:
            score -= 0.25 * opp_d
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]