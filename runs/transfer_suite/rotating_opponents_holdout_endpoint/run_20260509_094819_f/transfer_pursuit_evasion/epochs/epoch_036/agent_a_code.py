def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    role = ((observation.get("self_role", "") or "") + " " + (observation.get("environment_name", "") or "")).lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("evasion" in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def score_xy(x, y):
        dx = x - ox
        dy = y - oy
        dist = dx * dx + dy * dy
        if is_evader:
            best = dist
        else:
            best = -dist
        best = best - (x * 0 + y * 0)
        res = observation.get("resources", []) or []
        rc = observation.get("remaining_resource_count", None)
        if res and (rc is None or (isinstance(rc, int) and rc > 0)):
            for r in res:
                if isinstance(r, dict):
                    rx, ry = r.get("x", None), r.get("y", None)
                else:
                    rx, ry = (r[0], r[1]) if isinstance(r, (list, tuple)) and len(r) >= 2 else (None, None)
                if rx is None or ry is None:
                    continue
                rx, ry = int(rx), int(ry)
                if (rx, ry) in blocked:
                    continue
                tdx = x - rx
                tdy = y - ry
                rdist = tdx * tdx + tdy * tdy
                if is_evader:
                    best = best + (-rdist * 0.01)
                else:
                    best = best + (-rdist * 0.01)
        return best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_xy(nx, ny)
        if best_val is None or (v > best_val) or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]