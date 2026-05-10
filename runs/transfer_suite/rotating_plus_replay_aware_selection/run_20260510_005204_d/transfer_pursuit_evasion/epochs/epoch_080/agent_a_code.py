def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "")).lower()
    evader = ("evader" in role) or ("runner" in role) or ("evade" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # tie-break prefers staying centered away from obstacles
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_pen(x, y):
        pen = 0
        for dx, dy in moves[:-1]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in blocked:
                pen += 1
        return pen

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_now = dist2(nx, ny, ox, oy)
        far_corner = max(dist2(nx, ny, cx, cy) for cx, cy in corners)
        # predict opponent next best chase/escape by assuming it moves one step optimally
        opp_best = None
        opp_sign = 1 if evader else -1  # if we're evader, opponent pursues (min dist); else opponent evades (max dist)
        for odx, ody in moves:
            px, py = ox + odx, oy + ody
            if not inb(px, py) or (px, py) in blocked:
                continue
            val = dist2(px, py, nx, ny)
            if opp_best is None or (val < opp_best if evader else val > opp_best):
                opp_best = val
        if opp_best is None:
            opp_best = d_now
        # Score: if evader -> maximize future distance; else -> minimize future distance
        future = opp_best
        score = (-future if not evader else future) + 0.01 * far_corner - 0.02 * obstacle_pen(nx, ny)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]