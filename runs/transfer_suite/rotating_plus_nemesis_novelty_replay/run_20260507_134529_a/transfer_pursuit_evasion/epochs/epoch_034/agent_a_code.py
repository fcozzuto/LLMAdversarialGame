def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" not in self_role)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        capture = (nx == ox and ny == oy)  # capture_radius=0
        mobility = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                mobility += 1

        d = dist2(nx, ny)

        if is_evader:
            if capture:
                score = -10**12
            else:
                # Prefer moving away while keeping maneuverability
                score = d * 100 + mobility
                # Mildly discourage stepping into opponent if capture not immediate
                if d == 1:
                    score -= 50
        else:
            if capture:
                score = 10**12
            else:
                # Chase while preferring positions with more future options
                score = -d * 100 + mobility

        if best_score is None:
            best_score = score
            best_move = [dx, dy]
        else:
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move if ok(sx + best_move[0], sy + best_move[1]) else [0, 0]