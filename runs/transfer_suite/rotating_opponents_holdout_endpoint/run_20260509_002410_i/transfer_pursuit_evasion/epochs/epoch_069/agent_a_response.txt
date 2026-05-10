def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = observation.get("self_role", "pursuer")
    is_pursuer = (role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    sign = lambda v: 0 if v == 0 else (1 if v > 0 else -1)

    dx_dir = sign(ox - sx)
    dy_dir = sign(oy - sy)
    # tie-break order biased toward continuing the approach/escape direction
    pref = []
    for dx, dy in moves:
        score_dir = (dx == dx_dir) + (dy == dy_dir) + (dx == 0 and dy == 0)
        pref.append(((score_dir, -(dx * dx + dy * dy)), (dx, dy)))
    pref.sort(reverse=True)

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def center_bias(x, y):
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        return -((x - cx) * (x - cx) + (y - cy) * (y - cy))  # closer to center => larger

    def edge_bias(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)  # larger => more central
    def min_edge(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    best = None
    best_val = None
    for _, (dx, dy) in pref:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        dcur = dist2(sx, sy, ox, oy)
        dnxt = dist2(nx, ny, ox, oy)

        # Greedy pursuit/evasion with obstacle sensitivity and corner tendency for evader
        if is_pursuer:
            # reduce distance; avoid getting stuck near obstacles; slightly prefer center to cut off
            val = (dcur - dnxt) * 1000 + center_bias(nx, ny) * 0.5
            # penalty if adjacent cells blocked (local mobility)
            mob = 0
            for adx, ady in moves:
                tx, ty = nx + adx, ny + ady
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                    mob += 1
            val += mob * 0.25
        else:
            # maximize distance; prefer edges/corners; keep mobility
            val = (dnxt - dcur) * 1000 - edge_bias(nx, ny) * 0.4
            mob = 0
            for adx, ady in moves:
                tx, ty = nx + adx, ny + ady
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                    mob += 1
            val += mob * 0.15
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]