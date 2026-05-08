def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in role) or ("tag" in role) or ("hunter" in role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tx = int(observation.get("turn_index", 0))

    relx = ox - sx
    rely = oy - sy
    sxg = 1 if relx > 0 else (-1 if relx < 0 else 0)
    syg = 1 if rely > 0 else (-1 if rely < 0 else 0)
    adx = abs(relx); ady = abs(rely)

    # Predict zigzag evasion: alternate axis along which the evader "runs away"
    if (tx % 2) == 0:
        stepx = sxg if adx >= ady else 0
        stepy = syg if adx < ady else 0
    else:
        stepx = sxg if adx < ady else 0
        stepy = syg if adx >= ady else 0

    px = ox + stepx
    py = oy + stepy
    if not ok(px, py):
        px, py = ox, oy  # if blocked, assume it doesn't advance

    if is_pursuer:
        best = None
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ddx = nx - px
            ddy = ny - py
            val = -(ddx * ddx + ddy * ddy)
            # prefer not to stall when an improving move exists
            if dx == 0 and dy == 0:
                val -= 0.01
            if best is None or val > best:
                best = val
                best_move = [dx, dy]
        return best_move
    else:
        # Evader: maximize distance to predicted pursuer position (mirror of above)
        pred_px, pred_py = px, py
        best = None
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ddx = nx - pred_px
            ddy = ny - pred_py
            val = ddx * ddx + ddy * ddy
            if dx == 0 and dy == 0:
                val -= 0.01
            if best is None or val > best:
                best = val
                best_move = [dx, dy]
        return best_move