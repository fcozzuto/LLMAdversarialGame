def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If we are the pursuer, chase with mild "cut off" toward opponent's direction.
    # If evader, run toward the farthest corner from pursuer.
    dx_o = 0
    dy_o = 0
    if ox != sx:
        dx_o = 1 if ox > sx else -1
    if oy != sy:
        dy_o = 1 if oy > sy else -1
    predx = ox + dx_o
    predy = oy + dy_o

    if not inb(predx, predy):
        predx, predy = ox, oy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def far_corner():
        best = corners[0]
        bestv = -10**9
        for cx, cy in corners:
            v = dist(cx, cy, sx, sy)
            if v > bestv:
                bestv = v
                best = (cx, cy)
        return best

    evad_target = far_corner()

    best_move = [0, 0]
    if self_is_evader:
        # maximize distance from opponent while also preferring evad_target
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d1 = dist(nx, ny, ox, oy)
            d2 = dist(nx, ny, evad_target[0], evad_target[1])
            # prefer big separation first, then getting closer to target
            score = d1 * 100 - d2
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        # minimize distance to opponent, with a tie-break favoring moves that reduce distance to predicted position
        best_score = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d1 = dist(nx, ny, ox, oy)
            d2 = dist(nx, ny, predx, predy)
            # also add small penalty for moving away in both axes to avoid oscillations
            axis_pen = (0 if dx == 0 or (ox - sx) == 0 else 1) + (0 if dy == 0 or (oy - sy) == 0 else 1)
            score = d1 * 100 + d2 + axis_pen * 0.001
            if score < best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]