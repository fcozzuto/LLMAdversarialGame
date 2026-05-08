def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    dx_pref = clamp(ox - sx)
    dy_pref = clamp(oy - sy)

    # Alternate between direct chase/evasion and obstacle-biased sidestep to avoid getting stuck.
    phase = int(observation.get("turn_index", 0) or 0) % 2
    def pick_candidate_targets():
        if phase == 0:
            return [(dx_pref, dy_pref), (dx_pref, 0), (0, dy_pref), (0, 0)]
        return [(-dx_pref, dy_pref), (dx_pref, -dy_pref), (-dx_pref, -dy_pref), (0, 0)]

    best = (999999, 0, 0)
    cand_dirs = pick_candidate_targets()
    for ddx, ddy in cand_dirs + [m for m in moves if m not in cand_dirs]:
        nx, ny = sx + ddx, sy + ddy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        # Distance objective
        dist = cheb(nx, ny, ox, oy)
        # Obstacle pressure: prefer moves with more free neighbors (prevents dead-ends).
        free = 0
        for mdx, mdy in moves:
            tx, ty = nx + mdx, ny + mdy
            if inside(tx, ty) and (tx, ty) not in blocked:
                free += 1
        # If evader: maximize distance; if pursuer: minimize distance; tie-break with free space.
        score = (-dist if is_evader else dist) * 1000 + (free if is_evader else -free)
        # Deterministic final tie-break: prefer closer step to (dx_pref,dy_pref) then smallest (ddx,ddy).
        step_match = -(abs(ddx - dx_pref) + abs(ddy - dy_pref))
        score = score * 100 + step_match
        tup = (0 - score, ddx, ddy)
        if tup < best:
            best = tup

    # If all candidate moves blocked, stay still.
    return [int(best[1]), int(best[2])] if best[0] != 999999 else [0, 0]