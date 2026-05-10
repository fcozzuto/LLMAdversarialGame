def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("pursuer" in self_role) or (("pursuer" in opp_role) and ("evader" not in self_role))

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal_from(px, py):
        out = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                out.append((nx, ny))
        return out if out else [(px, py)]

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    def border_score(x, y):
        d = min(x, y, (w - 1) - x, (h - 1) - y)
        return d

    my_moves = legal_from(sx, sy)
    opp_moves = legal_from(ox, oy)  # used to limit computation deterministically

    best = None
    best_val = None

    for nx, ny in my_moves:
        # opponent chooses response extremizing distance (pursuer minimizes, evader maximizes)
        # determine who is opponent relative to us
        opp_is_pursuer = not self_is_pursuer
        best_opp = None
        best_opp_val = None
        for ex, ey in opp_moves:
            dist = cheb(nx, ny, ex, ey)
            val = dist if not opp_is_pursuer else -dist
            if best_opp_val is None or val > best_opp_val:
                best_opp_val = val
                best_opp = (ex, ey)

        dist_after = cheb(nx, ny, best_opp[0], best_opp[1])
        # primary: pursuer minimize distance; evader maximize distance
        primary = -dist_after if self_is_pursuer else dist_after
        # secondary: avoid borders if pursuer, prefer borders if evader
        bs = border_score(nx, ny)
        secondary = bs if self_is_pursuer else -bs
        val = primary * 1000 + secondary

        if best_val is None or val > best_val:
            best_val = val
            best = (nx, ny)

    dx = best[0] - sx
    dy = best[1] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]