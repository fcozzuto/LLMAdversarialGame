def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    srole = (observation.get("self_role", "") or "").lower()
    orole = (observation.get("opponent_role", "") or "").lower()
    self_evader = ("evad" in srole)
    opp_evader = ("evad" in orole)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def valid(x, y): return inb(x, y) and (x, y) not in obs

    def dist2(x, y, a=ox, b=oy):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def opp_objective(xo, yo, xself, yself):
        d = dist2(xo, yo, xself, yself)
        if xo == xself and yo == yself:
            return 10**9 if opp_evader else -10**9
        return d if opp_evader else -d

    def self_objective(xself, yself, xo, yo):
        d = dist2(xself, yself, xo, yo)
        if xself == xo and yself == yo:
            return 10**9 if not self_evader else -10**9
        return d if self_evader else -d

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        # opponent greedy response
        best_opp = None
        best_oppv = None
        for odx, ody in moves:
            mx, my = ox + odx, oy + ody
            if not valid(mx, my):
                mx, my = ox, oy
            v = opp_objective(mx, my, nx, ny)
            if best_opp is None or v > best_oppv or (v == best_oppv and (mx, my) < best_opp):
                best_opp, best_oppv = (mx, my), v
        mx, my = best_opp
        v = self_objective(nx, ny, mx, my)
        if best is None or v > bestv or (v == bestv and (nx, ny) < (best[0], best[1])):
            best, bestv = (nx, ny), v

    return [best[0] - sx, best[1] - sy]