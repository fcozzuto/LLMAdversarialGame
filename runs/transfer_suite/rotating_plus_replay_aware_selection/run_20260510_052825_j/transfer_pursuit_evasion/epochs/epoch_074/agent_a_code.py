def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def open_count(x, y):
        c = 0
        for ax, ay in moves:
            nx, ny = x + ax, y + ay
            if free(nx, ny):
                c += 1
        return c

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    pursuer = not evader

    best_move = (0, 0)
    if pursuer:
        # Chase while steering to reduce opponent mobility.
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            my_d = dist2(nx, ny)
            # Estimated next opponent mobility if we get closer (simple local heuristic).
            opp_mob = open_count(ox, oy)
            # Favor closer; slight penalty if opponent has many exits.
            score = (my_d, -opp_mob)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (nx - sx, ny - sy)
    else:
        # Flee: maximize distance, prefer moves with more own mobility, avoid moving into tight areas.
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            my_d = dist2(nx, ny)
            my_mob = open_count(nx, ny)
            # Mildly punish moves that give opponent similar/improved access by shrinking distance too quickly.
            # Also, if we reduce our mobility, avoid it.
            score = (-my_d, -my_mob)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (nx - sx, ny - sy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]