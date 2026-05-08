def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("run" in role) or ("away" in role) or ("escape" in role) or ("escape" in str(observation.get("opponent_role", "") or "").lower())

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def neigh_free_count(x, y):
        cnt = 0
        for ddx, ddy in deltas:
            nx, ny = x + ddx, y + ddy
            if in_bounds(nx, ny):
                cnt += 1
        return cnt

    best_move = [0, 0]
    best_val = None

    cur_d2 = dist2(sx, sy, ox, oy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d2 = dist2(nx, ny, ox, oy)
        free = neigh_free_count(nx, ny)
        center_d2 = dist2(nx, ny, cx, cy)

        if is_evader:
            # maximize distance; also prefer center and avoid tight spots
            val = (d2 - cur_d2) * 3.0 + free * 0.25 - center_d2 * 0.01
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            # minimize distance; also prefer more mobility to avoid corner traps
            val = -(d2 - cur_d2) * 3.0 + free * 0.25 - center_d2 * 0.002
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]