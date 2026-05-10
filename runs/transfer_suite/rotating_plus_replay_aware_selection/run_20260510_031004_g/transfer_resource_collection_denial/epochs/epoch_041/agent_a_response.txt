def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    env = observation.get("environment_name", "resource_collection")

    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not resources:
        return [0, 0]

    opp_better = 0
    # Choose target: minimize (dist_self - dist_opp), tie-break by (y,x) for determinism
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = ds - do
        if best is None or score < best[0] or (score == best[0] and (ry, rx) < (best[2], best[1])):
            best = (score, rx, ry)
            opp_better = do

    _, tx, ty = best

    dirs = [-1, 0, 1]
    candidates = []
    for dx in dirs:
        for dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                ds_next = cheb(nx, ny, tx, ty)
                ds_now = cheb(sx, sy, tx, ty)
                # Prefer moves that reduce our distance to target, and don't worsen relative race
                rel = (ds_next - cheb(ox, oy, tx, ty))
                # Tiny penalty for moving away
                away_pen = 0 if ds_next <= ds_now else (ds_next - ds_now) * 0.001
                # Prefer diagonal over orthogonal when equal, then deterministic tie by delta
                diag_bonus = -0.0001 if dx != 0 and dy != 0 else 0.0
                candidates.append((rel + away_pen + diag_bonus, -abs(dx) - abs(dy), dx, dy))
    # Staying still if needed
    if not candidates:
        return [0, 0]

    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]