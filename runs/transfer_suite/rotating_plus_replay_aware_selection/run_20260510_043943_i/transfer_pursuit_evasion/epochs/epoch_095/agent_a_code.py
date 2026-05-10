def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    opp_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))  # farthest corner from pursuer intent

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_to_opp = cheb(nx, ny, ox, oy)

        if is_evader:
            # Stay alive: maximize distance to opponent; when tied, head to farthest corner from opponent
            tgt = opp_corner  # corner farthest from opponent position (keeps away from zigzags)
            d_tgt = cheb(nx, ny, tgt[0], tgt[1])
            score = (d_to_opp, d_tgt, -abs(nx - sx) - abs(ny - sy))
            better = (best_score is None) or (score > best_score)
        else:
            # Pursue: minimize distance to opponent; when tied, prefer moving toward opponent's farthest corner
            tgt = opp_corner
            d_tgt = cheb(nx, ny, tgt[0], tgt[1])
            score = (-d_to_opp, d_tgt, -abs(nx - sx) - abs(ny - sy))
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]