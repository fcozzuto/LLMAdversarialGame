def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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
    is_evader = ("evad" in self_role) or (self_role == "evader")
    is_pursuer = ("purs" in self_role) or (self_role == "pursuer")
    if is_evader:
        mode = "evade"
    elif is_pursuer:
        mode = "pursue"
    else:
        mode = "pursue" if ("evad" in opponent_role) or (opponent_role == "evader") else "evade"

    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs

    dirs4 = [(-1,0),(1,0),(0,-1),(0,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    best_move = (0, 0)
    best_key = None

    # Deterministic tie-breaking: fixed evaluation order, keep first best.
    def neighbors_count(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        dpx, dpy = nx - ox, ny - oy
        dist2 = dpx*dpx + dpy*dpy

        # Encourage evader to run to the farthest corner; discourage getting trapped near obstacles.
        far_corner = 0
        for cx, cy in corners:
            ddx, ddy = nx - cx, ny - cy
            far_corner = max(far_corner, ddx*ddx + ddy*ddy)

        open_n = neighbors_count(nx, ny)  # more open is safer for evader
        # For pursuer, more open near self is slightly better to avoid local dead-ends while chasing.
        if mode == "evade":
            # Primary: maximize distance; Secondary: maximize openness + corner run
            key = (dist2, open_n, far_corner, -abs(nx - (w-1)) - abs(ny - (h-1)))
        else:
            # Pursue: minimize distance; Secondary: prefer moves with more escape routes for pursuer itself
            key = (-dist2, -open_n, far_corner)

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]