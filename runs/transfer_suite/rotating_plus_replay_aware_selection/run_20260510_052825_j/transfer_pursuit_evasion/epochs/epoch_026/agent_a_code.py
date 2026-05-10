def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    if ("evad" in self_role) or self_role == "evader":
        mode = "evade"
    elif ("purs" in self_role) or self_role == "pursuer":
        mode = "pursue"
    else:
        mode = "pursue" if (("evad" in opponent_role) or (opponent_role == "evader")) else "evade"

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    corners = [(0, 0), (0, h-1), (w-1, 0), (w-1, h-1)]
    target_corner = min(corners, key=lambda c: abs(c[0]-ox) + abs(c[1]-oy)) if mode == "pursue" else max(corners, key=lambda c: abs(c[0]-ox) + abs(c[1]-oy))

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        if mode == "pursue":
            # primary: minimize distance; secondary: bias toward nearest corner (helps wall-running evader capture via corner traps)
            score = (-d, -abs(nx-target_corner[0]) - abs(ny-target_corner[1]), -dx*dx - dy*dy)
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]
        else:
            # primary: maximize distance; secondary: steer to farthest corner from pursuer to escape walls
            score = (d, -abs(nx-target_corner[0]) - abs(ny-target_corner[1]), -dx*dx - dy*dy)
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]