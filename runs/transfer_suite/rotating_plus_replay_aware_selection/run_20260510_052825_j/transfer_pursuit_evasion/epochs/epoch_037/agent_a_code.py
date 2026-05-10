def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    if "evad" in self_role or self_role == "evader":
        mode = "evade"
    elif "purs" in self_role or self_role == "pursuer":
        mode = "pursue"
    else:
        mode = "pursue" if ("evad" in opponent_role or opponent_role == "evader") else "evade"

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if mode == "evade":
        # Prefer a corner farthest from pursuer, but avoid stepping into obstacles.
        best_corner = None
        best_cdist = -1
        for cx, cy in corners:
            cdist = abs(cx - ox) + abs(cy - oy)
            if cdist > best_cdist:
                best_cdist = cdist
                best_corner = (cx, cy)
        tx, ty = best_corner

        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            d_to_corner = abs(tx - nx) + abs(ty - ny)
            d_from_purs = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            score = (d_from_purs, d_to_corner, -abs(nx - ox) - abs(ny - oy))
            if best is None or score > best_score:
                best = [dx, dy]
                best_score = score
        return best if best is not None else [0, 0]

    # pursue: minimize distance to evader; if blocked, try alternative moves; deterministic tie-breaks by delta order
    best = [0, 0]
    best_d = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < (best[0], best[1])):
            best_d = d
            best = [dx, dy]
    return best