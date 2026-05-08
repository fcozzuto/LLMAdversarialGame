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
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" in self_role is False)
    if "pursuer" in self_role and "evader" not in self_role:
        is_evader = False

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist_metric(x, y):
        dx, dy = x - ox, y - oy
        return dx*dx + dy*dy

    best = None
    bestv = -10**18 if is_evader else 10**18

    # Evader: maximize distance; avoid stepping onto opponent.
    # Pursuer: minimize distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy:
            # If capture could happen, strongly avoid for evader; strongly prefer for pursuer.
            if is_evader:
                v = -10**14
            else:
                v = 10**14
        else:
            d2 = dist_metric(nx, ny)
            v = d2 if is_evader else -d2
        if best is None:
            best, bestv = [dx, dy], v
        else:
            if is_evader:
                if v > bestv:
                    best, bestv = [dx, dy], v
            else:
                if v > bestv:
                    best, bestv = [dx, dy], v

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]