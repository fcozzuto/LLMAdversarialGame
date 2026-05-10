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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_penalty(x, y):
        if not obstacles:
            return 0
        # discourage moving adjacent to obstacles more when evading/pursuing
        p = 0
        for bx, by in obstacles:
            d = abs(x - bx) + abs(y - by)
            if d == 0:
                return 10**6
            if d == 1:
                p += 3
            elif d == 2:
                p += 1
        return p

    # deterministic tie-break ordering
    order = {d: i for i, d in enumerate(dirs)}

    # If evader, aim for corner farthest from pursuer (opponent).
    # If pursuer, aim to reduce distance and avoid obstacles.
    best_move = [0, 0]
    best_score = None

    # pick target corner deterministically
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if self_is_evader:
        tx, ty = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
    else:
        tx, ty = ox, oy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if self_is_evader:
            # maximize distance from opponent, and progress toward chosen corner
            dist_opp = manh(nx, ny, ox, oy)
            dist_corner = manh(nx, ny, tx, ty)
            # small preference to reduce distance-to-corner (safer cornering)
            score = dist_opp * 10 - dist_corner - obstacle_penalty(nx, ny)
        else:
            # minimize distance to opponent; if cannot reach directly, use corner-bias to cut off
            dist_opp = manh(nx, ny, ox, oy)
            dist_corner = manh(nx, ny, ox, oy) - 0.1 * manh(nx, ny, tx, ty)
            score = -dist_opp * 10 - obstacle_penalty(nx, ny) + (-dist_corner * 0.01)

        if best_score is None:
            best_score = score
            best_move = [dx, dy]
        else:
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
            elif score == best_score:
                if order[(dx, dy)] < order[(best_move[0], best_move[1])]:
                    best_move = [dx, dy]

    return best_move if best_move != [0, 0] or legal(sx, sy) else [0, 0]