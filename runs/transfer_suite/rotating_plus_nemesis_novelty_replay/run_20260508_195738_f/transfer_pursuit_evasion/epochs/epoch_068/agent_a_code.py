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

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Predict opponent "next" by assuming it continues its last direction (from corners of the move space).
    # With no history, infer direction bias by nearest corner tendency: evasion_zigzag often flips axes.
    dx_o = 0
    if ox != sx:
        dx_o = 1 if ox > sx else -1
    dy_o = 0
    if oy != sy:
        dy_o = 1 if oy > sy else -1
    pred_ox = ox + dx_o
    pred_oy = oy + dy_o
    if not inb(pred_ox, pred_oy):
        pred_ox, pred_oy = ox, oy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: manh(c[0], c[1], pred_ox, pred_oy)) if self_is_evader else \
                   min(corners, key=lambda c: manh(c[0], c[1], pred_ox, pred_oy))

    best_move = (0, 0)
    best_val = None

    # Deterministic tie-break: keep first achieving best.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d_to_pred = manh(nx, ny, pred_ox, pred_oy)
        d_to_opp = manh(nx, ny, ox, oy)
        # Obstacle proximity penalty to avoid tight corridors.
        near_obs = 0
        for bx, by in obstacles:
            dd = abs(nx - bx) + abs(ny - by)
            if dd == 0:
                near_obs += 1000000
            elif dd == 1:
                near_obs += 5
            elif dd == 2:
                near_obs += 2

        # Corner bias.
        d_corner = manh(nx, ny, best_corner[0], best_corner[1])

        if self_is_evader:
            # Maximize survival: far from pursuer + keep progressing to "safe" corner.
            val = (d_to_pred * 10) + (d_to_opp * 3) - (d_corner * 1) - near_obs
        else:
            # Maximize capture likelihood: move closer to predicted pursuer with obstacle avoidance.
            val = -(d_to_pred * 10) - (d_to_opp * 3) - near_obs - (d_corner * 0.2)

        if best_val is None or (val > best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]