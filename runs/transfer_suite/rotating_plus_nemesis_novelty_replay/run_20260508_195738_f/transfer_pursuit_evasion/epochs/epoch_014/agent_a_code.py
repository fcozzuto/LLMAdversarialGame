def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    is_pursuer = ("purs" in self_role) or ("purs" in opp_role) or ("evader" not in self_role)

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def score_evader(nx, ny):
        d_after = dist2(nx, ny, ox, oy)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        corner_far = max(corners, key=lambda c: dist2(nx, ny, c[0], c[1]))
        corner_bonus = dist2(nx, ny, corner_far[0], corner_far[1]) / 10.0
        line_towards = 0
        stepx = 0 if ox == nx else (1 if ox > nx else -1)
        stepy = 0 if oy == ny else (1 if oy > ny else -1)
        if (nx + stepx, ny + stepy) in obstacles:
            line_towards = 8  # try to "hide" behind obstacle with respect to pursuer direction
        # discourage stepping into immediate "no-escape": count available moves from next position
        k = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty):
                k += 1
        escape = k  # higher is better
        return d_after + corner_bonus + line_towards + 1.5 * escape

    def score_pursuer(nx, ny):
        d_after = dist2(nx, ny, ox, oy)
        # prefer moves that reduce distance while also limiting opponent mobility
        k = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty):
                k += 1
        # also slightly bias towards moving to reduce your future escape (so you can maintain pressure)
        return -d_after + 0.2 * k

    best = (None, -10**18) if is_pursuer else (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_pursuer(nx, ny) if is_pursuer else score_evader(nx, ny)
        if sc > best[1] or (sc == best[1] and (best[0] is None or (dx, dy) < best[0])):
            best = ((dx, dy), sc)

    if best[0] is None:
        return [0, 0]
    return [best[0][0], best[0][1]]