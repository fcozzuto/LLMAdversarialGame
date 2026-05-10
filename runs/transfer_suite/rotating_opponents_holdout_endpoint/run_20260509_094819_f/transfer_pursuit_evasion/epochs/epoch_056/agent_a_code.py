def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "").lower()
    i_am_pursuer = ("purs" in role) or (role == "pursuer")

    tx, ty = ox, oy  # default
    if not i_am_pursuer:
        # Evader: deterministically run to farthest corner from pursuer, but avoid stepping into blocked cells.
        best = None
        for cx, cy in corners:
            if (cx, cy) in blocked:
                continue
            d = dist_cheb(cx, cy, ox, oy)
            if best is None or d > best[0] or (d == best[0] and (cx, cy) > (best[1], best[2])):
                best = (d, cx, cy)
        if best is not None:
            tx, ty = best[1], best[2]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if i_am_pursuer:
            # Pursuer: greedy to reduce distance; prefer moves that keep direction toward opponent.
            d = dist_cheb(nx, ny, ox, oy)
            # directional bonus
            dir_now = (1 if ox > sx else (-1 if ox < sx else 0), 1 if oy > sy else (-1 if oy < sy else 0))
            dir_new = (1 if ox > nx else (-1 if ox < nx else 0), 1 if oy > ny else (-1 if oy < ny else 0))
            align = (1 if dir_new == dir_now else 0)
            score = -d * 10 + align
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # Evader: greedy to increase distance to pursuer; bias toward chosen corner.
            d_fo = dist_cheb(nx, ny, ox, oy)
            d_tc = dist_cheb(nx, ny, tx, ty)
            # Prefer larger separation; break ties by getting closer to target corner
            score = d_fo * 10 - d_tc
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]