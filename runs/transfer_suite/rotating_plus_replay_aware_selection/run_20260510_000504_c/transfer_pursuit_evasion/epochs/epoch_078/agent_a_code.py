def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("evasion" in role)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def pick_moves():
        res = observation.get("resources", []) or []
        best = None
        bestd = None
        for r in res:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                x, y = int(r[0]), int(r[1])
                if ok(x, y):
                    d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
                    if best is None or d < bestd:
                        best, bestd = (x, y), d
        return best

    target = pick_moves()
    if target is None:
        tx, ty = ox, oy
    else:
        tx, ty = target

    best_score = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d_tar = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if is_evader:
            score = (-d_tar, -d_opp)  # flee from opponent while still preferring resource
        else:
            score = (d_tar, d_opp)   # approach resource/target; avoid proximity to opponent only secondarily
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]