def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("fugitive" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dist0 = man(sx, sy, ox, oy)
    if is_evader:
        tx, ty = max(corners, key=lambda c: (man(c[0], c[1], ox, oy), c[0] * 31 + c[1]))
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            corner_gain = man(nx, ny, tx, ty)
            near_pen = 0.0
            if d <= 1:
                near_pen = 100.0 * (1 - d)  # avoid being adjacent/at risk
            score = d + 0.15 * corner_gain - near_pen
            # small bias: don't move into squares that are closer than current if possible
            if d < dist0:
                score -= 0.35 * (dist0 - d)
            cand = (score, dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[1], best[2]] if best is not None else [0, 0]
    else:
        # Pursuer: greedily minimize distance; if tie, prefer moves that reduce opponent's best response
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d1 = man(nx, ny, ox, oy)
            # lookahead: assume opponent moves to maximize their distance (evader-like response)
            worst_opp = -10**9
            for odx, ody in moves:
                ax, ay = ox + odx, oy + ody
                if not valid(ax, ay):
                    continue
                worst_opp = max(worst_opp, man(nx, ny, ax, ay))
            # capture radius is 0; being on same cell ends game, so heavily reward d1==0
            score = (-d1) + (-0.03 * worst_opp)
            if d1 == 0:
                score += 10000.0
            cand = (score, -abs(dx), -abs(dy), dx, dy)  # deterministic tie-break
            if best is None or cand > best:
                best = cand
        return [best[3], best[4]] if best is not None else [0, 0]