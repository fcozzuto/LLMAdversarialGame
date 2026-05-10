def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    obst_list = list(obstacles)

    def obst_avoid(x, y):
        if not obst_list:
            return 0.0
        best = 10**9
        for ax, ay in obst_list:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        # Strongly discourage adjacency; lightly encourage moving away
        if best <= 1:
            return 30.0
        return 1.5 / best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        corner_dist = 0
        for cx, cy in corners:
            d = abs(cx - nx) + abs(cy - ny)
            if d > corner_dist:
                corner_dist = d

        avoid = obst_avoid(nx, ny)

        # Evader: maximize separation and stay away from obstacles; also drift toward farthest corner.
        # Pursuer: minimize separation; avoid obstacles to not waste moves.
        if is_evader:
            score = dist + 0.35 * corner_dist - 3.0 * avoid
        else:
            score = -dist - 1.0 * avoid + 0.05 * (-corner_dist)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move