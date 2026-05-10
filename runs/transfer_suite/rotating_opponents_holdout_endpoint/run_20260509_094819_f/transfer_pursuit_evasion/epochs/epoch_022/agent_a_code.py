def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def exits(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    # Wall-ish bias: prefer moving toward diagonally away from/into center, to vary behavior vs static cornering.
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        e = exits(nx, ny)
        # Center bias is deterministic and helps avoid getting funneled by wall-run patterns.
        center_dx = nx - cx
        center_dy = ny - cy
        center_term = 0
        if center_dx < 0: center_term -= 1
        elif center_dx > 0: center_term += 1
        if center_dy < 0: center_term -= 1
        elif center_dy > 0: center_term += 1

        if is_evader:
            # Maximize distance, keep mobility, slightly bias away from opponent axis by using sign of relative position.
            relx = nx - ox
            rely = ny - oy
            rel_term = (1 if relx > 0 else (-1 if relx < 0 else 0)) + (1 if rely > 0 else (-1 if rely < 0 else 0))
            score = (d, e, -abs(rel_term), -center_term)
            if best_score is None or score > best_score:
                best_score, best = score, [dx, dy]
        else:
            # Pursuer: minimize distance, avoid trapping (prefer more exits), and use center bias to cut off escape.
            score = (-d, e, center_term)
            if best_score is None or score > best_score:
                best_score, best = score, [dx, dy]

    if best is None:
        return [0, 0]
    return best