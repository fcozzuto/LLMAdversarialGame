def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))
        elif isinstance(a, dict) and "x" in a and "y" in a:
            obs.add((int(a["x"]), int(a["y"])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_target = None
    best_score = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            rx, ry = int(r["x"]), int(r["y"])
        else:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if ds == 0:
            return [0, 0]
        # Prefer resources where we are closer; heavily penalize ones opponent is closer to.
        lead = do - ds  # positive if we are closer
        score = ds - 2.5 * lead
        if best_score is None or score < best_score:
            best_score = score
            best_target = (rx, ry)

    if best_target is None:
        # No resources listed: move away/towards center deterministically.
        tx, ty = w // 2, h // 2
        dx = 1 if tx > sx else (-1 if tx < sx else 0)
        dy = 1 if ty > sy else (-1 if ty < sy else 0)
        nx, ny = sx + dx, sy + dy
        return [dx if inb(nx, ny) else 0, dy if inb(nx, ny) else 0]

    rx, ry = best_target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = man(nx, ny, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        # Evaluate: reduce distance to target, and also discourage stepping into opponent's immediate proximity.
        opp_close = max(0, 2 - man(nx, ny, ox, oy))  # 0..2
        lead_next = d_opp - d_self  # still prefer being closer
        val = d_self - 2.5 * lead_next + 1.2 * opp_close
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]